"""Genera resultados/Metodologia_modelo_Costco.pdf: explica qué se hizo, cómo y por qué.

Incluye notas numeradas que interpretan cada dato y un glosario para lectores sin formación
en economía o finanzas.

Uso (desde la carpeta proyecto_nuevo):  python src/generar_pdf_metodologia.py
Requiere: reportlab. Lee las tablas y gráficas que producen los notebooks 01 a 03.
"""
from pathlib import Path
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, ListFlowable, ListItem, HRFlowable)

BASE = Path(__file__).resolve().parents[1]
RES = BASE / "resultados"
OUT = RES / "Metodologia_modelo_Costco.pdf"

# Arial (Windows) cubre acentos, ñ y símbolos como − ≥ →
FONTS = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONTS / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS / "arialbi.ttf")))
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-BoldItalic")

AZUL = colors.HexColor("#1F4E79")
AZUL_CLARO = colors.HexColor("#DCE7F9")
GRIS = colors.HexColor("#4A5568")

S = {
    "titulo": ParagraphStyle("titulo", fontName="Arial-Bold", fontSize=22, leading=27, textColor=AZUL, spaceAfter=8),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Arial", fontSize=12, leading=16, textColor=GRIS, spaceAfter=4),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=15, leading=19, textColor=AZUL, spaceBefore=14,
                         spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, textColor=colors.black,
                         spaceBefore=9, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=10, leading=14, spaceAfter=6, alignment=TA_LEFT),
    "porque": ParagraphStyle("porque", fontName="Arial", fontSize=10, leading=14, spaceAfter=7, leftIndent=10,
                             backColor=colors.HexColor("#F1F5FB"), borderPadding=6),
    "nota": ParagraphStyle("nota", fontName="Arial-Italic", fontSize=8.5, leading=11, textColor=GRIS, spaceAfter=8),
    "fn": ParagraphStyle("fn", fontName="Arial", fontSize=7.8, leading=10, textColor=colors.HexColor("#2D3748"),
                         leftIndent=12, firstLineIndent=-12, spaceAfter=1.5),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=8.5, leading=11),
    "celda_b": ParagraphStyle("celda_b", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=colors.white),
    "formula": ParagraphStyle("formula", fontName="Arial", fontSize=10, leading=14, leftIndent=24, spaceAfter=8,
                              textColor=colors.HexColor("#14213D")),
    "gl_t": ParagraphStyle("gl_t", fontName="Arial-Bold", fontSize=9, leading=12),
    "gl_d": ParagraphStyle("gl_d", fontName="Arial", fontSize=9, leading=12),
}

# ---------- notas numeradas ----------
_contador = [0]
_pendientes = []


def N(texto):
    """Registra una nota de interpretación y devuelve su marcador en superíndice."""
    _contador[0] += 1
    _pendientes.append((_contador[0], texto))
    return f"<super><font color='#1F4E79'>{_contador[0]}</font></super>"


def notas():
    """Vacía las notas pendientes en un bloque bajo el párrafo o la tabla que las cita."""
    if not _pendientes:
        return []
    bloque = [HRFlowable(width="30%", thickness=0.5, color=GRIS, hAlign="LEFT", spaceBefore=1, spaceAfter=3)]
    bloque += [Paragraph(f"<super>{n}</super> {t}", S["fn"]) for n, t in _pendientes]
    _pendientes.clear()
    return [KeepTogether(bloque), Spacer(1, 6)]


def P(texto, estilo="p"):
    return Paragraph(texto, S[estilo])


def porque(texto):
    return P(f"<b>Por qué:</b> {texto}", "porque")


def lista(items):
    return ListFlowable([ListItem(P(t), leftIndent=12) for t in items], bulletType="bullet", start="•",
                        leftIndent=14, bulletFontName="Arial")


def tabla(filas, anchos, resaltar=None):
    # en el encabezado (fondo azul) los números de nota van en blanco para que se vean
    datos = [[Paragraph(str(c).replace("color='#1F4E79'", "color='#FFFFFF'"), S["celda_b"]) if i == 0
              else Paragraph(str(c), S["celda"]) for c in fila] for i, fila in enumerate(filas)]
    t = Table(datos, colWidths=[a * cm for a in anchos], repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8BEC9")),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for r in resaltar or []:
        estilo.append(("BACKGROUND", (0, r), (-1, r), AZUL_CLARO))
    t.setStyle(TableStyle(estilo))
    return t


def figura(nombre, ancho_cm, pie):
    img = Image(str(RES / "graficos" / nombre))
    escala = ancho_cm * cm / img.imageWidth
    img.drawWidth, img.drawHeight = img.imageWidth * escala, img.imageHeight * escala
    return KeepTogether([img, P(pie, "nota")])


def pie_pagina(canvas, doc):
    canvas.saveState()
    canvas.setFont("Arial", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2 * cm, 1.2 * cm, "Expansión de Costco en México · Metodología del modelo")
    canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def fmt(x, d=0):
    return f"{x:,.{d}f}"


# ---------- datos de los notebooks ----------
T = RES / "tablas"
logit = pd.read_csv(T / "02_logit_participacion.csv", index_col=0)
gamma = pd.read_csv(T / "02_gamma_intensidad.csv", index_col=0)
pmg = pd.read_csv(T / "02_propension_marginal.csv")
dzm = pd.read_csv(T / "02_demanda_oferta_zm.csv", index_col=0)
rob = pd.read_csv(T / "02_robustez_escenarios.csv", index_col=0)
vpn = pd.read_csv(T / "03_resultados_vpn_tir.csv")
fin = pd.read_csv(T / "03_fuentes_financiamiento.csv", index_col=0)
sens = pd.read_csv(T / "03_sensibilidad.csv", index_col=0)

h = []

# ================= PORTADA =================
h += [Spacer(1, 2.2 * cm),
      P("¿Dónde abrir el próximo Costco en México?", "titulo"),
      P("Metodología del modelo: qué se hizo, cómo se obtuvo, por qué se hizo así y qué quedó fuera", "subtitulo"),
      P("Hugo Cuellar y Valeria Castañeda · Licenciatura en Economía, UAEM · Finanzas Corporativas · noviembre de 2026",
        "subtitulo"),
      Spacer(1, 0.8 * cm),
      P("<b>En una frase.</b> Medimos cuánto gastan los hogares en clubes de precio con la ENIGH 2022, estimamos de qué "
        "depende ese gasto con un modelo econométrico, lo llevamos a cada municipio con el Censo 2020, lo comparamos con "
        "los clubes que ya existen (DENUE) y convertimos la demanda que queda sin atender en flujos de efectivo para "
        "calcular VPN y TIR. El resultado: <b>la zona metropolitana de Guadalajara, en su oriente (Tonalá y alrededores), "
        "es la única opción que crea valor en los dos escenarios que evaluamos</b>, siempre que la tienda cueste menos de "
        f"unos 48 millones de dólares{N('Es el monto con el que el proyecto apenas recupera la inversión y el costo del dinero (VPN igual a cero) en el escenario menos favorable para Guadalajara. Si la tienda cuesta menos, crea valor; si cuesta más, lo destruye. Está en dólares al tipo de cambio de 19.70 pesos por dólar del 25 de noviembre de 2026; equivale a unos 946 millones de pesos.')}."),
      *notas(),
      Spacer(1, 0.3 * cm),
      P("<b>Cómo leer este documento.</b> Cada paso tiene tres partes: qué hicimos, cómo lo obtuvimos y, en un recuadro "
        "azul, por qué lo hicimos de esa manera y no de otra. Cada cifra lleva un número pequeño en azul; la nota con ese "
        "número, justo debajo del párrafo o la tabla, explica cómo interpretarla y qué no significa. Los términos técnicos "
        "están explicados en el <b>glosario</b> al final (sección 12). Todas las cifras salen de los notebooks "
        "<i>01_datos_limpieza</i>, <i>02_modelo_econometrico</i> y <i>03_evaluacion_financiera</i> de la carpeta "
        "<i>proyecto_nuevo</i> del repositorio."),
      Spacer(1, 0.4 * cm),
      P("<b>Convenciones de unidades.</b> mdp = millones de pesos; mdd = millones de dólares. Salvo que se diga otra cosa, "
        "los pesos son de 2026 (ya incluyen la inflación hasta ese año), las cantidades de dinero son anuales y los "
        "porcentajes son tasas anuales. Un \"punto porcentual\" (pp) es la diferencia entre dos porcentajes: pasar de 8% a "
        "10% es subir 2 puntos porcentuales, que equivale a un aumento de 25%."),
      Spacer(1, 0.4 * cm),
      tabla([["Sección", "Contenido"],
             ["1", "La pregunta y por qué la planteamos por zona metropolitana"],
             ["2", "Por qué rehicimos el análisis desde cero"],
             ["3", "La ruta completa en siete pasos"],
             ["4", "Datos: fuentes, cómo se obtuvieron y cómo se limpiaron"],
             ["5", "Modelo econométrico de demanda"],
             ["6", "De hogares a municipios y zonas"],
             ["7", "Oferta actual y demanda no atendida"],
             ["8", "Evaluación financiera"],
             ["9", "Lo que no se hizo y las limitaciones"],
             ["10", "Resumen de decisiones"],
             ["11", "Cómo reproducir el análisis"],
             ["12", "Glosario"]], [2, 14]),
      PageBreak()]

# ================= 1 =================
h += [P("1. La pregunta y la unidad de análisis", "h1"),
      P(f"Costco planea 33 aperturas{N('Número de almacenes nuevos que Costco anunció para todo el mundo en su año fiscal 2027 (de septiembre de 2026 a agosto de 2027), según la llamada con analistas del 24 de septiembre de 2026. Incluye 5 reubicaciones de tiendas existentes. Es un plan, no un hecho.')} "
        f"en su año fiscal 2027, una de ellas en México, y tiene una estrategia de expansión a 20 años{N('Horizonte que la dirección de Costco México mencionó a la prensa (Expansión y El Economista, octubre de 2025). Lo usamos como plazo de evaluación del proyecto, no como pronóstico de cuánto durará la tienda.')} "
        "en el país. La pregunta del proyecto es en cuál de tres plazas conviene abrirla: Guadalajara, Monterrey o Querétaro."),
      *notas(),
      P(f"Definimos cada plaza como su <b>zona metropolitana</b>{N('Conjunto de municipios que forman una sola ciudad funcional porque la gente vive en uno y trabaja o compra en otro. Usamos la delimitación oficial de SEDATU, CONAPO e INEGI de 2020. En Querétaro excluimos Apaseo el Alto (Guanajuato), que pesa menos de 4% de la población de esa zona.')}: "
        "10 municipios en Guadalajara, 18 en Monterrey y 4 en Querétaro. Dentro de la zona ganadora bajamos al "
        "<b>municipio</b> para sugerir la ubicación."),
      *notas(),
      porque("un club de precio atrae compradores de toda la ciudad, no de un solo municipio ni de todo el estado. "
             "Usar el estado completo (por ejemplo, todo Jalisco) mezcla a Guadalajara con municipios rurales que nunca "
             "comprarían en un Costco; usar un solo municipio ignora que la gente de Tonalá puede ir al Costco de Zapopan. "
             "La zona metropolitana es la escala a la que compiten los clubes. El municipio sirve después para elegir el "
             "terreno dentro de ella.")]

# ================= 2 =================
h += [P("2. Por qué rehicimos el análisis desde cero", "h1"),
      P("La primera versión del proyecto (notebooks 01 a 05 de la carpeta <i>notebooks</i>) tenía tres problemas que "
        "impedían llegar a una decisión:"),
      lista(["<b>Medía ingreso, no demanda.</b> El modelo de la Fase 1 explicaba el logaritmo del ingreso con el estrato y "
             "el estado. Saber que Nuevo León tiene más ingreso no dice cuánto se gastaría en un Costco ni si ya hay "
             "suficientes clubes.",
             "<b>El logit de la Fase 2 era circular.</b> Su variable dependiente era 1 si en el municipio ya había un club. "
             "Eso mide dónde ya invirtieron los competidores, no dónde falta oferta: premia justo a los mercados saturados.",
             "<b>No conectaba con las finanzas.</b> No había un puente entre el resultado econométrico y los flujos de "
             "efectivo, así que no se podía calcular VPN ni TIR por plaza."]),
      porque("la rúbrica califica la comparación financiera (VPN, TIR, costo de capital) y el modelo econométrico tiene que "
             "alimentarla. Necesitábamos un modelo cuya salida fuera <b>pesos de demanda por zona</b>, que luego se "
             "convierten en ventas, costos y flujos. Por eso conservamos los datos ya descargados (ENIGH y DENUE), pero "
             "cambiamos la variable a explicar y el diseño completo.")]

# ================= 3 =================
h += [P("3. La ruta completa en siete pasos", "h1"),
      tabla([["Paso", "Qué se hace", "Herramienta", "Resultado"],
             ["1", "Medir el gasto de cada hogar en clubes de precio", "ENIGH 2022, tabla de gastos",
              f"90,102 hogares{N('Hogares entrevistados por el INEGI en todo el país para la ENIGH 2022. Es una muestra, no el total de hogares de México (que son unos 37.6 millones). Cada hogar de la muestra representa a cientos o miles de hogares parecidos, según su factor de expansión.')}; "
              f"7,425 compran en clubes{N('Hogares de la muestra que reportaron al menos una compra en tiendas con membresía durante los periodos de referencia de la encuesta (de una semana a seis meses, según el tipo de gasto). Un hogar que es socio de un club pero no compró en ese periodo aparece como no comprador, así que esta cifra subestima ligeramente a los usuarios de clubes.')}"],
             ["2", "Estimar de qué depende ese gasto", "Logit + GLM Gamma + MCO", "Efectos marginales, propensión marginal"],
             ["3", "Calcular la demanda de cada municipio", "Censo 2020 y 2010", "Pesos de demanda por municipio y zona"],
             ["4", "Escalar a ventas reales de la industria", "Costco México, Walmex",
              f"Factor de calibración k = 4.0{N('Las ventas reales de Costco México y Sam’s Club en 2025 son unas 4 veces lo que la ENIGH registra como gasto de los hogares en clubes. Ver la sección 6 para la explicación completa.')}"],
             ["5", "Medir la oferta actual", "DENUE + aperturas 2026",
              f"38 clubes en las tres zonas{N('Costco, Sam’s Club y City Club con más de 100 empleados dentro de las tres zonas metropolitanas: 13 en Guadalajara, 19 en Monterrey y 6 en Querétaro. Incluye Costco Escobedo (abrió en mayo de 2026) y Costco Corregidora (abre en diciembre de 2026). Hay otros 4 clubes en esos estados pero fuera de las zonas (por ejemplo, Puerto Vallarta y San Juan del Río).')}"],
             ["6", "Calcular la demanda no atendida y el ingreso marginal", "Modelo de reparto tipo Huff",
              "Ingreso nuevo para Costco por zona"],
             ["7", "Evaluar el proyecto", "WACC, flujos a 20 años", "VPN, TIR, inversión máxima"]],
            [1.2, 5.2, 4.3, 5.3]),
      *notas()]

# ================= 4 =================
h += [P("4. Datos: fuentes, cómo se obtuvieron y cómo se limpiaron", "h1"),
      tabla([["Fuente", "Qué tomamos", "Cómo se obtuvo"],
             ["INEGI, ENIGH 2022 (nueva serie)", "Gasto por lugar de compra, ingreso, bienes del hogar, factor de expansión",
              "Microdatos ya descargados por el equipo (tablas concentradohogar, hogares y gastoshogar)"],
             ["INEGI, Censo 2020 (ITER)", "Hogares y equipamiento de las viviendas por municipio",
              "Descarga directa de datos abiertos del INEGI, un archivo por estado (14, 19 y 22)"],
             ["INEGI, Censo 2010 (ITER)", "Hogares por municipio en 2010",
              "Descarga del archivo nacional; nos quedamos con los 3 estados"],
             [f"INEGI, DENUE (corte abril 2026){N('El DENUE es una foto de los negocios registrados a una fecha. La versión que usamos se actualizó en abril de 2026, así que no incluye negocios abiertos después (por eso agregamos Escobedo y Corregidora a mano) y puede incluir alguno que ya cerró.')}",
              "Ubicación y tamaño de Costco, Sam's Club y City Club", "Descarga masiva por estado"],
             ["Costco: Annual Report FY2025 y resultados FY2026",
              "Estados financieros, márgenes por segmento, inversión, almacenes", "PDF del portal de inversionistas de Costco"],
             ["Walmart de México, Informe 2025 (BMV)", "Ventas, número de Sam's Club, inflación 2023-2025", "PDF del informe anual"],
             ["Banxico (SIE)", "TIIE 28 días, tasa objetivo, tipo de cambio FIX, inflación",
              "Consulta de los cuadros CA51, CF373 y CP151 (25-nov-2026)"],
             ["Damodaran (NYU Stern)", "Beta del sector, prima de riesgo de México, tasa del Tesoro",
              "Tablas de enero y noviembre de 2026"]],
            [4.2, 6.2, 5.6]),
      *notas(),
      P("Limpieza (notebook 01)", "h2"),
      lista(["<b>Gasto en clubes.</b> En la tabla <i>gastoshogar</i> cada compra trae su lugar de compra. El código 9 es "
             "\"Tiendas con membresía\". Sumamos el gasto trimestral de ese lugar por hogar y lo multiplicamos por 4 para "
             f"tenerlo anual{N('El INEGI ya convierte cada gasto a su equivalente trimestral, aunque se haya preguntado por semana, mes o semestre, y lo expresa en pesos de agosto de 2022. Multiplicar por 4 supone que el gasto de ese trimestre se repite todo el año; no capta compras de temporada (por ejemplo, diciembre).')}. "
             "Los hogares sin compras ahí quedan con gasto cero.",
             "<b>Variables del hogar.</b> Las convertimos en indicadores de sí o no (1 o 0): tiene automóvil (auto, camioneta "
             "o pickup), internet, computadora, horno de microondas, lavadora y TV de paga; además el número de integrantes "
             "y si vive en una localidad de 100 mil habitantes o más.",
             "<b>Censo.</b> Tomamos el renglón de total municipal y calculamos la proporción de viviendas con cada bien. "
             "La proporción urbana es la población que vive en localidades de 100 mil habitantes o más.",
             "<b>Clubes.</b> En el DENUE los clubes aparecen como supermercados (código SCIAN 462111). Los identificamos por "
             "nombre y exigimos más de 100 empleados para excluir oficinas, centros de distribución y gasolineras. "
             "Agregamos a mano dos aperturas que el DENUE aún no registra: Costco Escobedo (mayo de 2026) y Costco "
             "Corregidora (diciembre de 2026)."]),
      *notas(),
      porque("elegimos solo variables que existen <b>con la misma definición en la ENIGH y en el Censo</b> (\"variables "
             "espejo\"). La ENIGH dice cómo compra un hogar, pero solo es representativa por estado; el Censo cubre todos "
             "los municipios, pero no pregunta por gasto. Si el modelo usara una variable que el Censo no tiene (por "
             "ejemplo, el ingreso exacto), no podríamos aplicarlo a cada municipio. Por eso el ingreso entra en un análisis "
             "aparte (propensión marginal) y no en el modelo que se proyecta.")]

# ================= 5 =================
def bloque_logit():
    nota_coef = N("Coeficiente del logit: mide el efecto en una escala técnica (logaritmo de los momios) que no se lee directamente como porcentaje. Sirve para ver el signo (positivo = aumenta la probabilidad de comprar) y para calcular las dos columnas de la derecha, que sí son interpretables.")
    nota_ee = N("Error estándar: qué tan preciso es el coeficiente. Como regla práctica, el valor verdadero está con 95% de confianza entre el coeficiente menos y más 1.96 errores estándar. Por ejemplo, para automóvil: entre 0.903 y 1.091. Que el intervalo no incluya el cero significa que el efecto es real y no casualidad.")
    nota_rm = N("Razón de momios: cuántas veces mayores son los momios de comprar (probabilidad de comprar entre probabilidad de no comprar) de un hogar con la característica, comparado con uno sin ella y con todo lo demás igual. Para automóvil, 2.71 significa momios 2.71 veces mayores. No significa que la probabilidad sea 2.71 veces mayor.")
    nota_em = N("Efecto marginal promedio, en puntos porcentuales: cuánto sube, en promedio, la probabilidad de comprar en clubes si el hogar tiene la característica, con todo lo demás igual. Automóvil +6.3 significa que, por ejemplo, un hogar con 5% de probabilidad pasaría a 11.3%. Como en promedio solo 8.4% de los hogares compra, 6.3 puntos es un efecto grande. Es una asociación estadística: no prueba que comprar un auto haga que el hogar vaya a Costco, sino que los hogares con auto compran más ahí.")
    filas_logit = [["Variable", f"Coeficiente{nota_coef}", f"Error estándar{nota_ee}", f"Razón de momios{nota_rm}",
                    f"Efecto marginal (pp){nota_em}"]]
    for var, r in logit.iterrows():
        filas_logit.append([var, f"{r['coeficiente']:.3f}", f"{r['error estándar (cluster upm)']:.3f}",
                            f"{r['razón de momios']:.2f}", f"{r['efecto marginal (puntos %)']:+.1f}"])
    nota_sig = N("\"Significativo al 1%\" quiere decir que, si en realidad la característica no tuviera ningún efecto, la probabilidad de obtener por casualidad un coeficiente tan alejado de cero sería menor a 1%. En esta tabla todos los p-valores son menores a 0.001.")
    nota_tam = N("El tamaño del hogar tiene efecto negativo: cada persona adicional reduce 0.4 puntos la probabilidad de comprar, manteniendo los mismos bienes. Una explicación probable es que un hogar más grande con los mismos bienes tiene menos ingreso por persona.")
    return [tabla(filas_logit, [5, 2.6, 2.8, 2.8, 3]),
            P(f"Todos los coeficientes son significativos al 1%{nota_sig}. El signo negativo del tamaño del hogar{nota_tam} es el único "
              "efecto que reduce la probabilidad.", "nota"),
            *notas()]


def bloque_gamma():
    nota_gamma = N("Cambio en el gasto: entre los hogares que sí compran en clubes, cuánto más (en %) gasta un hogar con la característica que uno sin ella, con todo lo demás igual. Automóvil +50.1% significa que, si un comprador sin auto gasta 10,000 pesos al año en clubes, uno con auto y el mismo perfil gasta unos 15,000. Se calcula como (e elevado al coeficiente − 1) × 100.")
    nota_p = N("p-valor: probabilidad de obtener un coeficiente tan alejado de cero si el efecto real fuera nulo. Por convención, menos de 0.05 se considera significativo. Internet (0.187) y tamaño del hogar (0.065) no lo son: no podemos afirmar que cambien el monto gastado, aunque sí cambian la probabilidad de comprar (tabla anterior).")
    filas_gamma = [["Variable", "Coeficiente", f"p-valor{nota_p}", f"Cambio en el gasto{nota_gamma}"]]
    for var, r in gamma.iterrows():
        filas_gamma.append([var, f"{r['coeficiente']:.3f}", f"{r['p-valor']:.3f}", f"{r['cambio % en gasto']:+.1f}%"])
    return [tabla(filas_gamma, [5.5, 3, 3, 4]), *notas()]


h += [PageBreak(), P("5. Modelo econométrico de demanda", "h1"),
      P("5.1 Especificación: un modelo de dos partes", "h2"),
      P(f"El 91.6%{N('Porcentaje de hogares del país, ya ponderado con el factor de expansión, que no reportó compras en tiendas con membresía. Es el complemento del 8.4% que sí compra.')} "
        "de los hogares no compra en clubes y gasta cero; el resto gasta cantidades muy distintas. Por eso separamos dos "
        "decisiones:"),
      *notas(),
      P("Parte 1 (¿compra?):  P(compra = 1 | X) = Λ(Xβ), un logit.", "formula"),
      P("Parte 2 (¿cuánto, si compra?):  E[gasto | compra = 1, X] = exp(Xγ), un GLM con distribución Gamma y enlace "
        "logarítmico.", "formula"),
      P("Gasto esperado del hogar:  E[gasto | X] = P(compra = 1 | X) × E[gasto | compra = 1, X].", "formula"),
      P("Cómo leer las fórmulas: P(compra = 1 | X) es la probabilidad de que un hogar con características X compre en "
        "clubes; E[gasto | ...] es el gasto promedio esperado; β y γ son los coeficientes que estima el modelo.", "nota"),
      P("Además estimamos un <b>MCO del gasto incondicional</b> (incluyendo los ceros) sobre las mismas variables. Es el que "
        "usamos para proyectar a municipios."),
      porque("una regresión lineal sobre una variable con 92% de ceros predice gastos negativos y mezcla dos decisiones que "
             "responden distinto: el auto influye mucho en <i>si</i> se compra, menos en <i>cuánto</i>. El modelo de dos "
             "partes es el estándar en microeconometría del consumo para este caso. El logit garantiza probabilidades entre "
             "0 y 1; la Gamma con enlace log garantiza gastos positivos y admite que el gasto varíe más entre hogares que "
             "gastan más, lo que se observa en los datos (heterocedasticidad)."),
      porque("para el paso a municipios usamos el MCO porque es <b>lineal</b>: el promedio de una función lineal es la función "
             "del promedio, así que basta con meter las proporciones del Censo para obtener el gasto medio del municipio sin "
             "sesgo. Con el logit, meter promedios en una función no lineal da un resultado sesgado. Comprobamos que las dos "
             f"rutas coinciden: el gasto promedio por estado que predicen tiene una correlación de 0.986{N('La correlación va de −1 a 1. Un valor de 0.986 entre lo que predicen el modelo de dos partes y el MCO para los 32 estados significa que ordenan a los estados casi exactamente igual. Por eso usar el MCO para proyectar no cambia las conclusiones.')} entre ellas."),
      *notas(),
      P("5.2 Estimación", "h2"),
      lista(["Todas las regresiones usan el <b>factor de expansión</b> de la ENIGH como ponderador, normalizado a media 1.",
             "Los errores estándar están <b>agrupados por unidad primaria de muestreo</b> (UPM), porque los hogares de una "
             "misma UPM se parecen entre sí y la ENIGH se levanta por conglomerados.",
             "Se estima con los <b>90,102 hogares del país</b>, no solo con los de los tres estados."]),
      porque(f"con solo los tres estados tendríamos unos 10,000 hogares y menos de 800 compradores{N('En la muestra hay 10,059 hogares de Jalisco, Nuevo León y Querétaro, de los cuales 785 compraron en clubes (198, 240 y 347, respectivamente).')}; "
             "con el país completo hay 7,425 compradores, lo que hace los coeficientes mucho más precisos. Las diferencias "
             "propias de cada estado se revisan después, en la prueba de robustez (escenario B)."),
      *notas(),
      P("5.3 Resultados de la parte 1 (logit): ¿quién compra?", "h2"),
      *bloque_logit(),
      P("Tener automóvil sube la probabilidad de comprar en clubes en 6.3 puntos, y tener computadora en 5.4. Es coherente "
        "con cómo funciona el formato: compras grandes que requieren coche y hogares de ingreso medio-alto (la computadora "
        "funciona como indicador de ingreso y escolaridad)."),
      P("5.4 Resultados de la parte 2 (GLM Gamma): ¿cuánto gasta quien compra?", "h2"),
      *bloque_gamma(),
      P("5.5 Propensión marginal y elasticidad ingreso", "h2"),
      P("Para responder qué pasa con el gasto en clubes cuando sube el ingreso, estimamos aparte:"),
      lista([f"<b>Propensión marginal a gastar en clubes:</b> {pmg.iloc[0, 3]:.2f} centavos{N('De cada peso adicional de ingreso anual, en promedio 1.35 centavos se gastan en clubes de precio (es decir, 13.50 pesos de cada 1,000 adicionales). Se obtiene comparando hogares con distinto ingreso en un mismo momento, no siguiendo a un hogar cuyo ingreso sube. Incluye a los hogares que no compran en clubes, por eso es pequeña.')} "
             f"de cada peso adicional de ingreso (Jalisco {pmg.iloc[1, 3]:.2f}, Nuevo León {pmg.iloc[2, 3]:.2f}, "
             f"Querétaro {pmg.iloc[3, 3]:.2f}{N('Propensión marginal estimada solo con los hogares de cada estado. En Querétaro un peso adicional de ingreso se traduce en más gasto en clubes que en Nuevo León; puede reflejar preferencias o qué tan cerca están los clubes de los hogares. Los errores estándar están en el notebook 02; las tres son significativas al 1%.')}).",
             f"<b>Elasticidad ingreso:</b> 0.65{N('Elasticidad: cambio porcentual del gasto en clubes cuando el ingreso cambia 1%. Con 0.65, si el ingreso de un hogar comprador sube 10%, su gasto en clubes sube 6.5%. Se mide solo entre los hogares que ya compran. Su error estándar es 0.04, así que el valor real está con 95% de confianza entre 0.58 y 0.72.')} "
             "entre los hogares que compran: es un bien normal (su consumo sube con el ingreso, pero menos que proporcionalmente).",
             f"<b>Por decil:</b> compra en clubes 1% de los hogares del decil más pobre y 32% del más rico{N('Los deciles dividen a los hogares en 10 grupos del mismo tamaño, ordenados por ingreso. El decil 1 es el 10% de hogares con menos ingreso (unos 54,000 pesos al año en promedio) y el decil 10 el 10% con más (unos 803,000). Los porcentajes son la proporción de hogares de cada grupo que reportó comprar en clubes.')}."]),
      *notas(),
      figura("02_deciles.png", 15.5, "Participación y gasto en clubes de precio por decil de ingreso (pesos de agosto de 2022). "
             "Fuente: ENIGH 2022."),
      P("5.6 Validación: ¿el modelo es confiable?", "h2"),
      lista([f"<b>AUC de 0.80 dentro de muestra y 0.799 ± 0.004 en validación cruzada de 5 partes</b>{N('El AUC va de 0.5 (el modelo no distingue mejor que una moneda al aire) a 1 (distingue perfectamente). Con 0.80, si se toma al azar un hogar que compra y uno que no, el modelo le asigna más probabilidad al que compra 8 de cada 10 veces. El ± 0.004 es cuánto varió el AUC entre las 5 particiones: muy poco, lo que indica un resultado estable.')}. "
             "Que el valor no baje fuera de muestra indica que el modelo no está sobreajustado.",
             f"<b>Pseudo R² de McFadden de 0.16</b>{N('Medida de ajuste para modelos de probabilidad. No se compara con el R² de una regresión lineal: en este tipo de modelos, valores entre 0.2 y 0.4 se consideran un ajuste excelente, y 0.16 es normal para datos de hogares, donde influyen muchos factores que la encuesta no mide.')}.",
             "<b>Calibración:</b> por decil de probabilidad predicha, la proporción que realmente compra es muy parecida a la "
             "predicha (gráfica de abajo).",
             f"<b>Multicolinealidad:</b> todos los factores de inflación de varianza (VIF) son menores a 1.6{N('El VIF indica si dos o más variables explicativas dicen casi lo mismo, lo que haría imprecisos sus coeficientes. Un VIF de 1 significa nada de traslape; se considera problemático a partir de 5 o 10. Con menos de 1.6, cada variable aporta información propia.')}.",
             f"<b>Heterocedasticidad:</b> la prueba de Breusch-Pagan la detecta (p &lt; 0.001){N('Significa que la dispersión del gasto no es igual para todos los hogares: varía más entre los que gastan más. No sesga los coeficientes, pero hace que los errores estándar normales sean incorrectos. Por eso usamos errores estándar robustos, que siguen siendo válidos en este caso.')}; "
             "por eso todos los errores estándar son robustos y agrupados."]),
      *notas(),
      figura("02_calibracion.png", 7.5, "Calibración del logit: cada punto es un decil de probabilidad predicha. Si el "
             "modelo estuviera perfectamente calibrado, todos los puntos caerían sobre la línea punteada."),
      ]

# ================= 6 =================
h += [PageBreak(), P("6. De hogares a municipios y zonas", "h1"),
      P("La demanda anual de clubes de cada municipio en 2026 se calcula así:"),
      P("Demanda<sub>m,2026</sub> = Hogares<sub>m,2026</sub> × Ĝ<sub>m</sub> × Inflación<sub>2022→2026</sub> × k",
        "formula"),
      lista(["<b>Ĝ<sub>m</sub></b>: gasto anual esperado por hogar con el perfil del municipio, aplicando el MCO a las "
             f"proporciones del Censo 2020{N('Por ejemplo, para el municipio de Guadalajara el modelo estima 3,508 pesos de 2022 por hogar al año antes de calibrar. No es lo que gasta un hogar concreto: es el promedio de todos los hogares del municipio, incluyendo los que no compran nada.')}.",
             f"<b>Hogares 2026</b>: hogares del Censo 2020 proyectados con la tasa de crecimiento anual 2010-2020 de cada municipio{N('Es una estimación, no un conteo. Supone que entre 2020 y 2026 cada municipio siguió creciendo al mismo ritmo que en 2010-2020. En municipios de crecimiento muy rápido (García, NL, 11.6% anual) puede sobreestimar.')}.",
             f"<b>Inflación 2022→2026</b>: INPC 4.7% (2023), 4.2% (2024), 3.7% (2025) y 3.75% (2026, anual a octubre). "
             f"Factor acumulado: 1.174{N('Un peso de agosto de 2022 equivale a 1.174 pesos de 2026: lo que costaba 100 pesos cuesta unos 117. Las tasas de 2023 a 2025 vienen del Informe 2025 de Walmex (que cita al INEGI) y la de 2026 de Banxico.')}.",
             "<b>k = 4.0</b>: factor de calibración a las ventas reales de la industria."]),
      *notas(),
      porque("la ENIGH capta bien <i>quién</i> compra y cómo cambia el gasto entre hogares, pero se queda corta en el "
             "<i>nivel</i>: solo registra compras de hogares (no de negocios con membresía, que son una parte grande de "
             f"Costco y Sam's) y los hogares subdeclaran gasto. Expandida al país, la ENIGH da unos 80,400 millones de pesos de 2025{N('Gasto total en tiendas con membresía de todos los hogares del país según la ENIGH 2022 (68,000 mdp), llevado a precios de 2025 y ajustado por el crecimiento de hogares de 2022 a 2025 (supuesto de 1.5% anual).')}, "
             f"mientras que Costco México (104,328 millones) más Sam's Club (21.6% de los 1,011,598 millones de Walmex) vendieron 322,800 millones{N('Ventas totales de la industria de clubes de precio en México en 2025, sin City Club. La cifra de Costco incluye ventas en línea y gasolina; la de Sam’s se estimó como 21.6% de los ingresos totales de Walmex, porcentaje que reporta su informe de sostenibilidad 2025. Ambas cifras se tomaron de notas que citan la fuente original y conviene verificarlas.')}. "
             "Escalamos todo por k = 322,800 / 80,400 ≈ 4.0. Como k es igual para todas las zonas, <b>no cambia el orden "
             "entre ellas</b>: solo pone la demanda en la escala de las ventas reales, que es la que importa para los flujos. "
             "Excluimos City Club porque no publica ventas; eso hace k más pequeño y la calibración, conservadora."),
      *notas(),
      porque("proyectamos hogares con el crecimiento 2010-2020 del INEGI porque las proyecciones municipales de CONAPO no "
             "estaban disponibles para descarga. Para 2026 son solo 6 años de proyección. En la evaluación financiera, a "
             "20 años, usamos un crecimiento más prudente: la mitad del ritmo 2010-2020 en los años 1 a 10 y una cuarta "
             "parte en los años 11 a 20.")]

# ================= 7 =================
def bloque_brecha():
    n_dem = N("Demanda: lo que gastarían al año en clubes de precio los hogares de la zona (y, por la calibración, los negocios que compran ahí) si se comportaran como el promedio nacional de hogares con su mismo perfil. Millones de pesos de 2026.")
    n_cap = N("Capacidad actual: lo que venderían al año los clubes que ya existen en la zona si cada uno vendiera lo mismo que el promedio de su cadena en México. Es una aproximación: las tiendas reales venden más o menos que el promedio.")
    n_bre = N("Brecha: demanda menos capacidad. Positiva = hay más demanda que oferta (gasto que hoy se queda sin atender o se atiende lejos). Negativa = sobra oferta. La brecha A de Guadalajara (+4,259 mdp) equivale a unas 1.65 tiendas Costco promedio.")
    n_cob = N("Cobertura: capacidad entre demanda. 0.83 significa que los clubes actuales cubren 83% de la demanda estimada; 1.09 significa que hay 9% más capacidad que demanda.")
    filas_brecha = [["Zona", "Hogares 2026", "Clubes", f"Demanda{n_dem}", f"Capacidad actual{n_cap}", f"Brecha A{n_bre}",
                     "Brecha B", f"Cobertura A / B{n_cob}"]]
    for z, r in dzm.iterrows():
        filas_brecha.append([z, fmt(r.hogares_2026), int(r.clubes), fmt(r.demanda_2026), fmt(r.capacidad_2026),
                             f"{r.demanda_no_atendida:+,.0f}", f"{rob.loc[z, 'B · Brecha (millones)']:+,.0f}",
                             f"{r.indice_cobertura:.2f} / {rob.loc[z, 'B · Cobertura']:.2f}"])
    return [tabla(filas_brecha, [2.5, 2.0, 1.7, 1.9, 2.3, 1.8, 1.8, 2.3], resaltar=[1]),
            P("Millones de pesos de 2026, salvo hogares y clubes.", "nota"), *notas()]


h += [P("7. Oferta actual y demanda no atendida", "h1"),
      P(f"La capacidad de venta de los clubes existentes se calcula con la venta promedio de cada cadena: un Costco en México vende unos 2,577 millones de pesos al año{N('104,328 mdp de ventas de Costco México en 2025 (Expansión 500) entre 42 tiendas, más 3.75% de inflación para llevarlo a 2026. Es un promedio que incluye ventas en línea y gasolina; una tienda concreta puede vender bastante más o menos.')} "
        f"y un Sam's Club unos 1,288 millones{N('Ventas estimadas de Sam’s Club en 2025 (21.6% de los ingresos de Walmex) entre 176 clubes, más inflación 2026. Un Sam’s vende en promedio la mitad que un Costco.')}. "
        "City Club no publica cifras; lo tratamos como un Sam's."),
      *notas(),
      porque("tratar a City Club como un Sam's probablemente <b>sobreestima</b> la competencia, porque sus clubes son más "
             "pequeños. Preferimos errar hacia el lado conservador: si aun así una zona tiene demanda sin atender, el "
             "resultado es más confiable."),
      *bloque_brecha(),
      P("Dos escenarios: por qué hay un A y un B", "h2"),
      P("El <b>escenario A</b> usa solo el perfil de los hogares. El <b>escenario B</b> agrega un efecto propio de cada "
        f"estado, estimado con efectos fijos: los hogares de Querétaro gastan 882 pesos al año más de lo que predice su perfil, y los de Nuevo León 853 menos{N('Pesos de agosto de 2022 por hogar al año, antes de aplicar la calibración k. Es la diferencia promedio entre lo que gastan los hogares de ese estado y lo que gastaría un hogar con el mismo perfil en el resto del país. El de Querétaro y el de Nuevo León son estadísticamente significativos; el de Jalisco (−297) no lo es al 5%.')}."),
      *notas(),
      porque("el efecto fijo estatal puede reflejar dos cosas que no podemos separar con estos datos: preferencias "
             "distintas (que sí son demanda) o más o menos oferta cerca (que no lo es: en un estado con pocos clubes se "
             "compra menos aunque se quiera). Como no sabemos cuál pesa más, presentamos los dos escenarios y buscamos una "
             "decisión que funcione en ambos. Guadalajara es la única zona con brecha positiva en los dos."),
      figura("02_brecha_zm.png", 14, "Demanda estimada contra capacidad de los clubes existentes, escenario A, miles de "
             "millones de pesos de 2026."),
      P("Dentro de la zona de Guadalajara, el municipio con más demanda sin club propio es <b>Tonalá</b>: "
        f"187,000 hogares, 2,298 millones de pesos de demanda al año y ningún club de precio{N('Hogares estimados para 2026 y demanda calibrada en pesos de 2026. Que Tonalá no tenga club no significa que sus hogares no compren: hoy viajan a clubes de municipios vecinos. La tienda nueva capturaría esas compras más cerca de casa y la demanda que hoy no se realiza por la distancia.')}. "
        "Le siguen el propio municipio de Guadalajara y San Pedro Tlaquepaque. Los tres Costcos actuales están en "
        "Zapopan, Tlajomulco y Guadalajara, al poniente y al sur."),
      *notas()]

# ================= 8 =================
b = vpn[vpn.capex == "base"].set_index(["escenario", "zona"])
lo = vpn[vpn.capex == "bajo"].set_index(["escenario", "zona"])
def bloque_vpn():
    n_im = N("Ingreso marginal: ventas anuales adicionales que obtiene Costco en toda la zona por abrir la tienda, ya descontado lo que la tienda nueva les quita a los Costcos existentes. Millones de pesos de 2026, en el nivel que alcanza la tienda cuando madura (año 3).")
    n_max = N("Inversión máxima: lo más que Costco podría gastar en terreno, construcción y equipo para que el proyecto todavía recupere su costo de capital (VPN = 0). Un valor negativo significa que la tienda pierde valor aunque el terreno y el edificio fueran gratis.")
    n_vpn = N("VPN (valor presente neto): cuánto valor crea hoy el proyecto, en millones de pesos de 2026, después de recuperar la inversión y de pagar el 11.34% anual que exigen los inversionistas. +403 significa que el proyecto vale 403 mdp más de lo que cuesta. Un VPN negativo no significa que la tienda tenga pérdidas contables: significa que rinde menos que el costo de capital.")
    n_tir = N("TIR (tasa interna de rendimiento): rendimiento anual del proyecto. Se compara con el WACC (11.34%): si la TIR es mayor, el proyecto crea valor. Guadalajara A con 35 mdd rinde 16.6% anual; \"negativa\" significa que no se recupera ni lo invertido.")
    n_68 = N("Mismo cálculo con una inversión de 67.9 mdd (1,338 mdp), punto medio del rango verificable. Con ese monto ninguna zona crea valor; por eso la decisión depende de construir una tienda de menor costo.")
    filas_vpn = [["Zona, escenario", f"Ingreso marginal 2026{n_im}", f"Inversión máxima (mdd){n_max}", f"VPN con 35 mdd{n_vpn}",
                  f"TIR con 35 mdd{n_tir}", f"VPN con 68 mdd{n_68}"]]
    for (e, z) in [("A", "Guadalajara"), ("B", "Guadalajara"), ("B", "Querétaro"), ("A", "Querétaro"), ("A", "Monterrey"),
                   ("B", "Monterrey")]:
        tir = lo.loc[(e, z), "TIR"]
        filas_vpn.append([f"{z}, {e}", fmt(b.loc[(e, z), "ingreso_marginal_2026_mdp"]), f"{b.loc[(e, z), 'capex_max_mdd']:.1f}",
                          f"{lo.loc[(e, z), 'VPN_mdp']:+,.0f}", "negativa" if pd.isna(tir) or tir < 0 else f"{tir:.1%}",
                          f"{b.loc[(e, z), 'VPN_mdp']:+,.0f}"])
    return [tabla(filas_vpn, [3.3, 2.7, 2.7, 2.4, 2.4, 2.5], resaltar=[1, 2]),
            P("Millones de pesos salvo donde se indica.", "nota"), *notas()]


h += [PageBreak(), P("8. Evaluación financiera", "h1"),
      P("8.1 Costo de capital (WACC) en pesos", "h2"),
      P("K<sub>e</sub><super>USD</super> = R<sub>f</sub> + β<sub>L</sub> × ERP<sub>México</sub> = 4.94% + 0.808 × 6.69% = 10.35%",
        "formula"),
      P("K<sub>e</sub><super>MXN</super> = (1 + K<sub>e</sub><super>USD</super>) × (1 + π<sub>MX</sub>) / (1 + π<sub>EU</sub>) − 1 = 11.43%",
        "formula"),
      lista([f"<b>R<sub>f</sub> = 4.94%</b>{N('Tasa libre de riesgo: rendimiento anual del bono del Tesoro de Estados Unidos a 10 años al 1 de noviembre de 2026 (Damodaran). Es lo que gana un inversionista sin correr riesgo, y el punto de partida de cualquier tasa de descuento.')}",
             f"<b>β<sub>L</sub> = 0.808</b>{N('Beta: qué tanto se mueve el negocio con el mercado en general. 1 = igual que el mercado; menos de 1 = más estable. Partimos de la beta de supermercados (0.80, Damodaran, enero de 2026) y la ajustamos por la poca deuda de Costco (1.4% de su valor de mercado). Un supermercado es menos riesgoso que el promedio porque la gente compra comida aun en crisis.')}",
             f"<b>ERP<sub>México</sub> = 6.69%</b>{N('Prima de riesgo de capital para México: rendimiento extra que exige un inversionista por invertir en acciones en México en lugar de bonos sin riesgo. Se compone de 4.23% de un mercado maduro más 2.46% de riesgo país (Damodaran, enero de 2026).')}",
             f"<b>K<sub>e</sub> = 10.35% en dólares y 11.43% en pesos</b>{N('Costo del capital propio: rendimiento anual mínimo que esperan los accionistas de Costco por un proyecto en México. En pesos es más alto porque se espera que el peso pierda valor frente al dólar al ritmo de la diferencia de inflación (3% en México contra 2% en Estados Unidos, las metas de Banxico y de la Reserva Federal).')}"]),
      *notas(),
      P("La deuda cuesta TIIE + 1 punto, 5.29% después de impuestos. Con el peso de cada fuente, el "
        f"<b>WACC en pesos es 11.34%</b>{N('Costo promedio ponderado de capital: rendimiento anual mínimo, en pesos y en términos nominales (incluye inflación), que debe dar la tienda para que valga la pena. Es casi igual al costo del capital propio porque Costco casi no usa deuda (1.4% de su financiamiento).')}."),
      *notas(),
      porque("los ingresos de la tienda son en pesos, así que la tasa de descuento también debe estar en pesos. Banxico no "
             "nos dio un rendimiento verificable del Bono M a 10 años, así que construimos la tasa en dólares (donde "
             "Damodaran publica todo: tasa libre de riesgo, prima de mercado y riesgo país de México) y la pasamos a pesos "
             "con la paridad de Fisher, usando las metas de inflación de Banxico (3%) y de la Reserva Federal (2%). Es el "
             "método estándar para descontar flujos en moneda local cuando la tasa local no es confiable."),
      P("8.2 Ingreso marginal: la canibalización importa", "h2"),
      P("Una tienda nueva no solo vende: también le quita clientes a los Costcos que ya hay en la zona. Por eso el ingreso "
        "relevante es el <b>ingreso marginal para Costco</b>: lo que venden todas sus tiendas de la zona después de abrir, "
        "menos lo que vendían antes."),
      P("ΔR = S<sub>1</sub> × (n + 1)·w / (W + w) − S<sub>0</sub> × n·w / W,  con S = mín(demanda, capacidad)", "formula"),
      P("Aquí n es el número de Costcos actuales, w la venta de un Costco promedio y W la capacidad total de clubes; S<sub>0</sub> "
        "y S<sub>1</sub> son las ventas totales de clubes antes y después de abrir. Cada club se lleva una parte de las ventas "
        "proporcional a su tamaño (modelo de reparto tipo Huff con igual accesibilidad)."),
      porque("si ignoráramos la canibalización, Monterrey parecería atractiva porque tiene la mayor demanda total. Pero ahí "
             f"35 de cada 100 pesos que vendería la tienda nueva se los quitaría a otros Costcos{N('En Monterrey la tienda nueva vendería unos 2,171 mdp al año (escenario A), pero 755 mdp de esa venta saldrían de los otros 4 Costcos de la zona. Para Costco, solo 1,416 mdp son venta nueva. En Querétaro (escenario A) la canibalización es de 50 de cada 100 pesos; en Guadalajara (escenario A), cero.')}. "
             "El 10-K de Costco reconoce este riesgo explícitamente. En Guadalajara, en cambio, la tienda atiende demanda que "
             "hoy no tiene club."),
      *notas(),
      P("8.3 Flujo de efectivo", "h2"),
      tabla([["Concepto", "Supuesto", "Fuente o razón"],
             ["Horizonte", "20 años + valor terminal creciendo al 3%",
              f"Estrategia de Costco en México a 20 años; 3% = inflación meta, sin crecimiento real{N('El valor terminal resume en un solo número el valor de la tienda después del año 20, suponiendo que sus flujos crecen al 3% anual para siempre (solo inflación, sin crecimiento real). Es un supuesto conservador para una tienda que seguiría operando.')}"],
             ["Margen bruto", "12.03% del ingreso marginal",
              f"Segmento Other International de Costco, FY2025{N('De cada 100 pesos que Costco vende de más, 87.97 se van a pagar la mercancía y le quedan 12.03 (incluye las cuotas de membresía). Es el margen de los almacenes de Costco fuera de Estados Unidos y Canadá en su año fiscal 2025, no un dato exclusivo de México.')}"],
             ["Gastos de operación", "6.83% de la venta de la tienda",
              f"Mismo segmento, sin depreciación{N('Sueldos, luz, renta de sistemas, publicidad y demás gastos de operar el almacén: 6.83 pesos de cada 100 que pasan por sus cajas.')}"],
             ["Mantenimiento", "0.88% de la venta de la tienda", "Depreciación del segmento"],
             ["Capital de trabajo", "−1.1% de las ventas (entrada de efectivo)",
              f"Costco cobra antes de pagar a proveedores (balance FY2026){N('Costco vende la mercancía antes de pagarla a sus proveedores, así que crecer le genera efectivo en lugar de consumirlo: por cada 100 pesos de ventas nuevas recibe 1.10 pesos de financiamiento de proveedores. Es poco, pero tiene el signo contrario al de la mayoría de los negocios.')}"],
             ["Arranque", "80% el año 1, 90% el año 2",
              f"Las tiendas nuevas tardan en madurar (10-K){N('Supuesto propio: la tienda vende 80% de su nivel normal el primer año y 90% el segundo, mientras atrae socios. El 10-K de Costco advierte que los almacenes nuevos tardan en madurar, pero no da porcentajes.')}"],
             ["Inversión", "35.4 a 100.4 mdd; 30% terreno",
              f"Activo fijo neto por almacén y adiciones por apertura del segmento; Escobedo{N('Cota baja: valor en libros del activo fijo del segmento (6,189 mdd) entre sus 175 almacenes; está depreciado, así que una tienda nueva costaría más. Cota alta: lo que el segmento invirtió en activo fijo en FY2025 (703 mdd) entre sus 7 aperturas; incluye remodelaciones y otros proyectos, así que sobreestima. Coincide con los 100 mdd reportados para Escobedo, la tienda más grande de Costco en América Latina. El 30% de terreno es un supuesto: el terreno no se deprecia.')}"],
             ["Impuestos", "ISR 30%", "Ley del ISR"]], [3.2, 5.3, 7.5]),
      *notas(),
      porque("el margen bruto se aplica al ingreso marginal (la venta realmente nueva), pero los gastos de operación al total "
             "que pasa por las cajas de la tienda, porque el personal, la luz y el mantenimiento dependen del volumen que "
             "atiende el almacén, sea venta nueva o canibalizada. Usamos márgenes del segmento <i>Other International</i> "
             "porque Costco no publica México por separado y ese segmento lo incluye."),
      P("8.4 La regla de decisión: inversión máxima justificable", "h2"),
      P("Costco no publica cuánto invierte por tienda. Por eso, además del VPN con distintos montos, calculamos la "
        "<b>inversión máxima con la que el VPN es cero</b>: el máximo que Costco puede gastar en la tienda sin destruir valor."),
      *bloque_vpn(),
      figura("03_capex_maximo.png", 14, "Inversión máxima justificable por zona y escenario, frente al rango de inversión "
             "verificable (líneas punteadas)."),
      porque("reportar un solo VPN dependería de un número (la inversión) que no conocemos. La inversión máxima convierte la "
             "incertidumbre en una regla clara para quien decide: <i>abre en Guadalajara si la tienda cuesta menos de 48 "
             "millones de dólares</i>. Además, el VPN es lineal en la inversión, así que este cálculo es exacto."),
      P("8.5 Sensibilidad", "h2"),
      P("Movimos cada supuesto y recalculamos el VPN del escenario B con la inversión base. Lo que más pesa es la demanda "
        f"(±20% mueve el VPN de Guadalajara entre {sens.loc['Demanda −20%', 'Guadalajara']:,.0f} y "
        f"{sens.loc['Demanda +20%', 'Guadalajara']:,.0f} millones{N('Con la inversión base (67.9 mdd) el VPN de Guadalajara B es −354 mdp. Si la demanda real fuera 20% menor que la estimada, bajaría a −1,299; si fuera 20% mayor, subiría a −176. Que siga negativo confirma que, con esa inversión, la tienda no se paga; con una más barata sí.')}) "
        "y la inversión. Guadalajara supera a Querétaro en las 12 pruebas; Monterrey solo sube de lugar con 20% menos "
        "demanda, prueba en la que las tres zonas pierden valor."),
      *notas(),
      P("8.6 Fuentes de financiamiento", "h2"),
      tabla([["Opción", "Costo antes de impuestos", f"Costo después de impuestos{N('Los intereses de una deuda se pueden deducir de impuestos (escudo fiscal): con un ISR de 30%, pagar 7.55% de interés cuesta en realidad 5.29%. Los recursos propios no tienen ese beneficio, por eso su costo no cambia.')}",
              f"Riesgo cambiario{N('Riesgo de que el peso se deprecie: si Costco se endeuda en dólares y sus ingresos son en pesos, cada peso vale menos dólares para pagar la deuda. El 6.57% del bono en dólares ya incluye la depreciación esperada, pero no la inesperada.')}"]] +
            [[i, f"{r.iloc[0]:.2%}", f"{r.iloc[1]:.2%}", r.iloc[2]] for i, r in fin.iterrows()], [5.5, 3.2, 3.2, 4.1]),
      *notas(),
      P(f"Un crédito en pesos por la inversión base, a 10 años, implica un pago anual fijo de 195.4 millones de pesos{N('Anualidad: pago constante que cubre intereses y capital, calculado para un préstamo de 1,338 mdp a TIIE + 1 (7.55%) a 10 años. El primer año 101 mdp son intereses y 94 abono a capital; con los años la proporción se invierte. La tabla completa está en resultados/tablas/03_amortizacion_credito.csv.')}. "
        f"Como referencia de valuación, un bono con cupón de 5% a 10 años vale 103.63 por cada 100 de valor nominal si el mercado exige 4.54%, y 95.94 si exige 5.54%{N('Cuando la tasa que exige el mercado baja de la tasa del cupón, el bono vale más de su valor nominal (sobre la par), y cuando sube, vale menos (bajo la par). Es un ejemplo ilustrativo, no un bono real de Costco.')}."),
      *notas(),
      porque("comparamos el bono en dólares en pesos con la paridad de tasas: pagar en dólares cuesta más en pesos porque se "
             "espera que el peso se deprecie al ritmo del diferencial de inflación. Recomendamos recursos propios porque "
             f"Costco tiene 20,207 millones de dólares en caja{N('Efectivo y equivalentes al 30 de agosto de 2026, según el comunicado de resultados del año fiscal 2026. Es dinero de toda la empresa, no solo de México.')}; "
             "el crédito en pesos solo tendría sentido como cobertura cambiaria, porque calza la moneda de la deuda con la de "
             "los ingresos."),
      *notas()]

# ================= 9 =================
h += [PageBreak(), P("9. Lo que no se hizo y las limitaciones", "h1"),
      P("Ser explícitos sobre esto es parte del rigor. Ninguna de estas limitaciones cambia el orden de las zonas en las "
        "pruebas que pudimos hacer, pero conviene conocerlas antes de defender el resultado."),
      tabla([["Lo que no se hizo", "Por qué", "Qué efecto puede tener"],
             ["Usar la ENIGH 2024", "Ya teníamos la 2022 completa y procesada; ambas son de la nueva serie y comparables",
              "El nivel de gasto podría ser algo mayor; el orden entre zonas no debería cambiar"],
             ["Usar proyecciones municipales de CONAPO", "No encontramos un archivo descargable verificable",
              "Usamos el crecimiento 2010-2020 del INEGI, atenuado en las finanzas"],
             ["Modelar distancias y tiempos de traslado", "Requiere un sistema de información geográfica y red de calles",
              "El reparto de mercado supone igual accesibilidad dentro de la zona"],
             ["Precio del terreno por ciudad", "No encontramos una fuente pública verificable",
              "Por eso la decisión se expresa como inversión máxima, no como un solo VPN"],
             ["Márgenes de Costco México", "Costco no los publica por separado", "Usamos el segmento Other International"],
             ["Ventas de City Club", "Soriana no las publica", "Tratarlo como un Sam's sobreestima la competencia (conservador)"],
             ["Rendimiento del Bono M a 10 años", "La página de Banxico no lo mostraba de forma verificable",
              "El WACC se construyó en dólares y se pasó a pesos con Fisher"],
             ["Separar preferencia de oferta en el efecto estatal", "La ENIGH no dice a qué distancia está el club más cercano",
              "Se presentan los escenarios A y B"],
             ["Abrir directamente algunas cifras de prensa", "Se tomaron de notas que citan la fuente",
              "Verificar antes de entregar: Expansión 500, 21.6% de Sam's en Walmex, calificaciones"]],
            [4.3, 5.7, 6]),
      Spacer(1, 0.3 * cm),
      P("También decidimos <b>no usar</b> el parque vehicular registrado (INEGI) ni la ENOE. El parque vehicular refleja "
        "dónde se registran los vehículos (incluidas flotillas), no dónde viven los dueños; el Censo mide directamente si "
        "la vivienda tiene auto. La ENOE solo es representativa por ciudad y no aporta variables de gasto.")]

# ================= 10 =================
h += [P("10. Resumen de decisiones", "h1"),
      tabla([["Decisión", "Alternativa descartada", "Razón"],
             ["Medir demanda con el gasto en \"tiendas con membresía\"", "Usar el ingreso como sustituto",
              "Mide directamente lo que se quiere predecir"],
             ["Modelo de dos partes", "Una sola regresión lineal", "92% de ceros; dos decisiones distintas"],
             ["Variables espejo ENIGH ↔ Censo", "Incluir el ingreso en el modelo de proyección",
              "El Censo no mide ingreso; sin espejo no hay proyección municipal"],
             ["MCO lineal para proyectar", "Meter promedios en el logit", "Evita el sesgo de agregación"],
             ["Estimar con todo el país", "Solo los tres estados", "7,425 compradores en lugar de menos de 800"],
             ["Calibrar a ventas reales (k = 4.0)", "Usar el nivel de la ENIGH",
              "La ENIGH no capta compras de negocios y subdeclara"],
             ["Zona metropolitana como unidad", "Estado o municipio", "Es la escala a la que compiten los clubes"],
             ["Dos escenarios (A y B)", "Elegir uno", "No se puede separar preferencia de oferta"],
             ["Ingreso marginal con canibalización", "Ventas de la tienda", "Lo que importa es la venta nueva para Costco"],
             ["WACC en dólares pasado a pesos", "Bono M directo", "Fuentes verificables y método estándar"],
             ["Inversión máxima como regla", "Un solo VPN", "La inversión por tienda no es pública"],
             ["Corregidora como oferta existente", "Ignorarla", "Abre en diciembre de 2026, antes que la tienda evaluada"]],
            [5, 4.5, 6.5])]

# ================= 11 =================
h += [P("11. Cómo reproducir el análisis", "h1"),
      lista(["Colocar los datos crudos en <i>proyecto_nuevo/data/raw/</i> (ENIGH 2022, Censo 2010 y 2020, DENUE, reportes de "
             "Costco y Walmex), con los nombres que indica el README.",
             "Abrir los notebooks desde la carpeta <i>proyecto_nuevo/notebooks</i> y correrlos en orden: 01, 02 y 03.",
             "Las tablas quedan en <i>resultados/tablas</i>, las gráficas en <i>resultados/graficos</i> y los flujos con "
             "fórmulas de VPN y TIR en <i>resultados/tablas/03_flujos_costco.xlsx</i>.",
             "Este PDF se regenera con <i>python src/generar_pdf_metodologia.py</i>."])]

# ================= 12 GLOSARIO =================
GLOSARIO = [
    ("Datos y fuentes", [
        ("INEGI", "Instituto Nacional de Estadística y Geografía: el organismo oficial que levanta encuestas y censos en México."),
        ("ENIGH", "Encuesta Nacional de Ingresos y Gastos de los Hogares (INEGI). Pregunta a una muestra de hogares cuánto ganan, en qué gastan y dónde compran. La usamos en su edición 2022."),
        ("Censo de Población y Vivienda", "Conteo de todas las personas y viviendas del país (INEGI), cada 10 años. Dice cuántos hogares hay en cada municipio y qué bienes tienen sus viviendas, pero no cuánto gastan."),
        ("ITER", "\"Principales resultados por localidad\" del Censo: la tabla con los totales de cada municipio y localidad."),
        ("DENUE", "Directorio Estadístico Nacional de Unidades Económicas (INEGI): lista de negocios con su ubicación, actividad y número aproximado de empleados."),
        ("SCIAN", "Sistema de Clasificación Industrial de América del Norte: código que identifica la actividad de un negocio. Los clubes de precio aparecen como 462111, supermercados."),
        ("Microdatos", "Respuestas individuales de cada hogar de una encuesta (anónimas), en lugar de los totales ya publicados."),
        ("Muestra", "Parte de la población que se entrevista para estimar cómo es toda la población."),
        ("Factor de expansión", "Número de hogares reales que representa cada hogar de la muestra. Sirve para que los promedios reflejen a todo el país y no solo a quienes respondieron."),
        ("Ponderar", "Calcular promedios dando a cada hogar un peso igual a su factor de expansión."),
        ("Unidad primaria de muestreo (UPM)", "Grupo de viviendas cercanas que la encuesta selecciona junto. Los hogares de una misma UPM se parecen entre sí."),
        ("Decil", "Cada uno de los 10 grupos del mismo tamaño en que se dividen los hogares ordenados por ingreso. El decil 1 es el 10% más pobre y el decil 10 el 10% más rico."),
        ("Zona metropolitana", "Conjunto de municipios que funcionan como una sola ciudad porque la gente se mueve entre ellos para vivir, trabajar y comprar."),
        ("Variables espejo", "Características que se miden igual en la ENIGH y en el Censo (por ejemplo, si la vivienda tiene auto). Permiten pasar lo aprendido en la encuesta a cada municipio."),
    ]),
    ("Econometría y estadística", [
        ("Econometría", "Uso de la estadística para medir relaciones económicas con datos reales, por ejemplo, cuánto cambia el gasto cuando cambia el ingreso."),
        ("Variable dependiente", "Lo que se quiere explicar (aquí, si un hogar compra en clubes y cuánto gasta)."),
        ("Variable explicativa", "Característica que se usa para explicar la variable dependiente (auto, internet, tamaño del hogar, etc.)."),
        ("Regresión", "Técnica que estima cuánto cambia una variable cuando cambia otra, manteniendo las demás constantes."),
        ("MCO (mínimos cuadrados ordinarios)", "La regresión lineal más común: ajusta la línea que minimiza los errores al cuadrado."),
        ("Logit", "Regresión para variables de sí o no. Estima la probabilidad de que algo ocurra (aquí, que el hogar compre en clubes), siempre entre 0 y 1."),
        ("GLM Gamma", "Modelo lineal generalizado con distribución Gamma: regresión para cantidades siempre positivas cuya dispersión crece con su tamaño, como el gasto."),
        ("Modelo de dos partes", "Combinación de un logit (¿compra?) y un modelo de gasto (¿cuánto, si compra?). Se usa cuando muchos hogares tienen gasto cero."),
        ("Coeficiente", "Número que estima el modelo para cada variable explicativa. Indica la dirección y la fuerza de su relación con la variable dependiente."),
        ("Momios", "Probabilidad de que algo pase dividida entre la probabilidad de que no pase. Si la probabilidad es 20%, los momios son 0.2 / 0.8 = 0.25."),
        ("Razón de momios", "Cuántas veces mayores son los momios de un grupo comparado con otro (por ejemplo, hogares con auto contra sin auto)."),
        ("Efecto marginal", "Cuánto cambia el resultado (aquí, la probabilidad de comprar) cuando cambia una característica, con todo lo demás igual."),
        ("Punto porcentual (pp)", "Diferencia entre dos porcentajes. De 8% a 10% hay 2 puntos porcentuales, que es un aumento de 25%."),
        ("Error estándar", "Medida de la incertidumbre de un coeficiente. Entre más pequeño, más preciso."),
        ("Errores estándar robustos y agrupados", "Errores estándar corregidos para que sigan siendo válidos cuando la dispersión no es igual entre hogares y cuando hogares de un mismo grupo se parecen."),
        ("p-valor", "Probabilidad de obtener un resultado tan alejado de cero si en realidad no hubiera ningún efecto. Menos de 0.05 se considera significativo."),
        ("Significancia estadística", "Que un efecto sea tan claro que es muy improbable que se deba a la casualidad de la muestra. No dice si el efecto es grande o importante."),
        ("Intervalo de confianza", "Rango donde, con cierta confianza (normalmente 95%), está el valor verdadero de un coeficiente."),
        ("Correlación", "Medida de qué tan juntas se mueven dos variables, de −1 (opuestas) a 1 (iguales). No implica que una cause la otra."),
        ("Heterocedasticidad", "Cuando la dispersión de los datos no es igual para todos (aquí, el gasto varía más entre hogares que gastan más)."),
        ("Prueba de Breusch-Pagan", "Prueba estadística que detecta heterocedasticidad."),
        ("Multicolinealidad", "Cuando dos o más variables explicativas dicen casi lo mismo, lo que vuelve imprecisos sus coeficientes."),
        ("VIF (factor de inflación de varianza)", "Medida de multicolinealidad. Menos de 5 se considera aceptable."),
        ("AUC", "Área bajo la curva ROC: qué tan bien distingue un modelo entre dos grupos (compradores y no compradores). 0.5 = azar; 1 = perfecto."),
        ("Pseudo R² de McFadden", "Medida de ajuste para modelos de probabilidad como el logit. No se compara con el R² de una regresión lineal."),
        ("Validación cruzada", "Probar el modelo con datos que no usó para estimarse: se divide la muestra en partes, se estima con unas y se evalúa con otra."),
        ("Sobreajuste", "Cuando un modelo se aprende de memoria la muestra y funciona mal con datos nuevos."),
        ("Calibración (de un modelo)", "Que las probabilidades que predice el modelo coincidan con lo que realmente pasa."),
        ("Efecto fijo", "Variable que captura todo lo que distingue a un grupo (aquí, cada estado) y que el modelo no mide directamente."),
        ("Sesgo de agregación", "Error que aparece al aplicar un modelo no lineal a promedios en lugar de a cada individuo."),
        ("Robustez", "Que una conclusión se mantenga al cambiar supuestos o métodos razonables."),
    ]),
    ("Economía", [
        ("Demanda", "Cantidad que los consumidores quieren y pueden comprar. Aquí, el gasto anual que harían los hogares en clubes de precio."),
        ("Oferta", "Capacidad de venta de los negocios que ya existen. Aquí, lo que pueden vender los clubes de la zona."),
        ("Demanda no atendida (brecha)", "Diferencia entre demanda y oferta: gasto que hoy no encuentra un club cercano."),
        ("Cobertura", "Oferta entre demanda. Menos de 1 indica que falta oferta."),
        ("Propensión marginal a gastar", "Fracción de cada peso adicional de ingreso que se gasta en algo."),
        ("Elasticidad ingreso", "Cambio porcentual del gasto en un bien cuando el ingreso cambia 1%."),
        ("Bien normal", "Bien cuyo consumo sube cuando sube el ingreso. Si sube más que proporcionalmente (elasticidad mayor a 1) se llama bien de lujo."),
        ("Inflación", "Aumento general de los precios. Se mide con el INPC."),
        ("INPC", "Índice Nacional de Precios al Consumidor (INEGI): mide cómo cambian los precios de lo que compran los hogares."),
        ("Pesos constantes / pesos de 2026", "Cantidades expresadas a precios de un mismo año para poder compararlas sin el efecto de la inflación."),
        ("Calibración (k)", "Factor que ajusta la demanda de la ENIGH para que su total coincida con las ventas reales de la industria."),
        ("Canibalización", "Ventas que una tienda nueva le quita a otras tiendas de la misma empresa."),
        ("Modelo de Huff", "Modelo que reparte las compras de una zona entre las tiendas según su tamaño (y, en su versión completa, su distancia)."),
        ("Club de precio / tienda con membresía", "Tienda que vende en volumen a precio bajo solo a sus socios, que pagan una cuota anual (Costco, Sam's Club, City Club)."),
        ("Nearshoring", "Traslado de fábricas a países cercanos a su mercado; en México ha impulsado a Monterrey y Querétaro."),
        ("Estrés hídrico", "Situación en la que la demanda de agua se acerca o supera a la disponible."),
    ]),
    ("Finanzas", [
        ("Flujo de efectivo", "Dinero que realmente entra y sale del proyecto cada año."),
        ("Ingreso marginal", "Ingreso adicional que se obtiene por hacer algo más, en este caso, por abrir una tienda."),
        ("Costo marginal", "Costo adicional de hacer algo más, en este caso, de operar la tienda nueva y pagar su inversión."),
        ("VPN (valor presente neto)", "Suma de todos los flujos de efectivo del proyecto traídos a valor de hoy con la tasa de descuento, menos la inversión. Positivo = el proyecto crea valor."),
        ("TIR (tasa interna de rendimiento)", "Rendimiento anual que da el proyecto. Si es mayor que el costo de capital, el proyecto crea valor."),
        ("Valor del dinero en el tiempo", "Un peso hoy vale más que un peso mañana, porque hoy se puede invertir y ganar intereses."),
        ("Tasa de descuento", "Tasa con la que se convierten flujos futuros a valor de hoy. Aquí es el WACC."),
        ("Costo de capital", "Rendimiento mínimo que exigen quienes financian a la empresa (accionistas y acreedores)."),
        ("WACC", "Costo promedio ponderado de capital: promedio del costo de la deuda y del capital propio, según cuánto pesa cada uno."),
        ("CAPM", "Modelo de valuación de activos de capital: calcula el rendimiento que exigen los accionistas como tasa libre de riesgo más beta por prima de riesgo."),
        ("Tasa libre de riesgo", "Rendimiento de una inversión sin riesgo de impago, normalmente un bono de gobierno (aquí, el del Tesoro de EE. UU. a 10 años)."),
        ("Beta", "Qué tanto se mueve una empresa o sector con el mercado. Beta desapalancada: sin el efecto de la deuda; apalancada: con él."),
        ("Prima de riesgo de capital", "Rendimiento extra que exige un inversionista por comprar acciones en lugar de bonos sin riesgo."),
        ("Riesgo país", "Rendimiento extra que se exige por invertir en un país con más riesgo económico o político que uno maduro."),
        ("Paridad de Fisher (internacional)", "Relación que dice que la diferencia de tasas entre dos países refleja su diferencia de inflación. Sirve para pasar una tasa en dólares a pesos."),
        ("Tipo de cambio FIX", "Tipo de cambio peso-dólar que publica Banxico cada día hábil."),
        ("Depreciación (del peso)", "Pérdida de valor del peso frente al dólar."),
        ("TIIE", "Tasa de Interés Interbancaria de Equilibrio (Banxico): referencia de los créditos en pesos."),
        ("Tasa objetivo", "Tasa de interés que fija Banxico para controlar la inflación."),
        ("Banxico", "Banco de México, el banco central del país."),
        ("Inversión (capex)", "Gasto en terreno, construcción y equipo para abrir la tienda."),
        ("Inversión máxima justificable", "Inversión con la que el VPN es exactamente cero: el máximo que se puede gastar sin destruir valor."),
        ("Depreciación (contable)", "Reparto del costo de un activo (edificio, equipo) a lo largo de su vida útil. No es salida de efectivo, pero reduce impuestos."),
        ("Capital de trabajo", "Dinero que se necesita para operar el día a día (inventarios menos lo que se debe a proveedores)."),
        ("Margen bruto", "Lo que queda de cada peso vendido después de pagar la mercancía."),
        ("Gastos de operación (SG&A)", "Gastos de vender y administrar: sueldos, luz, sistemas, publicidad."),
        ("EBITDA", "Utilidad antes de intereses, impuestos, depreciación y amortización: lo que genera la operación."),
        ("EBIT / NOPAT", "EBIT: utilidad de operación. NOPAT: utilidad de operación después de impuestos."),
        ("ISR", "Impuesto sobre la renta: 30% de la utilidad para las empresas en México."),
        ("Escudo fiscal", "Ahorro de impuestos porque los intereses de la deuda se pueden deducir."),
        ("Anualidad", "Serie de pagos iguales a intervalos regulares, como las mensualidades de un crédito."),
        ("Costo anual equivalente (CAE)", "La inversión convertida en un pago anual fijo a lo largo de su vida, usando la tasa de descuento."),
        ("Amortización", "Pago del capital de una deuda a lo largo del tiempo."),
        ("Valor terminal", "Valor de todos los flujos después del último año proyectado, resumido en un solo número."),
        ("Periodo de recuperación descontado", "Años que tarda el proyecto en recuperar la inversión, contando el valor del dinero en el tiempo."),
        ("Índice de rentabilidad (IR)", "Valor presente de los flujos entre la inversión. Mayor que 1 = crea valor."),
        ("Análisis de sensibilidad", "Cambiar un supuesto a la vez para ver cuánto cambia el resultado."),
        ("Escenario", "Conjunto de supuestos coherentes con el que se calcula un resultado (aquí, A y B)."),
        ("Bono / cupón / rendimiento", "Bono: deuda que una empresa o gobierno vende a inversionistas. Cupón: interés fijo que paga. Rendimiento: tasa que exige el mercado, que determina su precio."),
        ("CEBURE (certificado bursátil)", "Bono de deuda emitido en la bolsa mexicana."),
        ("Calificación crediticia (AA)", "Opinión de una calificadora (S&P, Fitch, Moody's, DBRS) sobre la capacidad de pagar deudas. AA es muy alta, solo debajo de AAA."),
        ("BMV / BIVA / CNBV", "Bolsa Mexicana de Valores, Bolsa Institucional de Valores y Comisión Nacional Bancaria y de Valores (el supervisor)."),
        ("10-K / Annual Report", "Informe anual que las empresas que cotizan en EE. UU. entregan a la SEC, el regulador de valores."),
        ("Año fiscal (FY)", "Año contable de la empresa. El de Costco va de septiembre a agosto: FY2026 terminó el 30 de agosto de 2026."),
        ("Segmento Other International", "División de Costco que agrupa sus almacenes fuera de EE. UU. y Canadá: México, Japón, Reino Unido, Corea, Australia, Taiwán, China, España, Francia, Suecia, Islandia y Nueva Zelanda."),
    ]),
]
h += [PageBreak(), P("12. Glosario", "h1"),
      P("Definiciones en lenguaje sencillo de los términos que aparecen en el documento, agrupadas por tema y en el orden "
        "en que conviene leerlas.")]
for tema, terminos in GLOSARIO:
    h.append(P(tema, "h2"))
    filas = [[Paragraph(t, S["gl_t"]), Paragraph(d, S["gl_d"])] for t, d in terminos]
    tg = Table(filas, colWidths=[4.6 * cm, 11.4 * cm])
    tg.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LINEBELOW", (0, 0), (-1, -1), 0.3, colors.HexColor("#D5DAE1")),
                            ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
    h.append(tg)

h += [Spacer(1, 0.5 * cm),
      P("Fuentes principales: INEGI (ENIGH 2022, Censos de Población y Vivienda 2010 y 2020, DENUE abril 2026); Costco "
        "Wholesale Corporation (Annual Report FY2025 y comunicado de resultados FY2026); Walmart de México (Informe 2025); "
        "Banxico (SIE, 25-nov-2026); A. Damodaran, NYU Stern (enero y noviembre de 2026); Mexico News Daily (2025).", "nota")]

assert not _pendientes, "Quedaron notas sin imprimir"
doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                        bottomMargin=2 * cm, title="Metodología del modelo: expansión de Costco en México",
                        author="Hugo Cuellar y Valeria Castañeda")
doc.build(h, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print(f"PDF generado: {OUT} ({_contador[0]} notas)")
