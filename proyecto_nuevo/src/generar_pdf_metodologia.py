"""Genera resultados/Metodologia_modelo_Costco.pdf: explica qué se hizo, cómo y por qué.

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
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle, ListFlowable, ListItem)

BASE = Path(__file__).resolve().parents[1]
RES = BASE / "resultados"
OUT = RES / "Metodologia_modelo_Costco.pdf"

# Arial (Windows) cubre acentos, ñ y símbolos como − ≥ →
FONTS = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONTS / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONTS / "arialbd.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Italic", str(FONTS / "ariali.ttf")))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", str(FONTS / "arialbi.ttf")))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("Arial", normal="Arial", bold="Arial-Bold", italic="Arial-Italic", boldItalic="Arial-BoldItalic")

AZUL = colors.HexColor("#1F4E79")
AZUL_CLARO = colors.HexColor("#DCE7F9")
GRIS = colors.HexColor("#4A5568")

S = {
    "titulo": ParagraphStyle("titulo", fontName="Arial-Bold", fontSize=22, leading=27, textColor=AZUL, spaceAfter=8),
    "subtitulo": ParagraphStyle("subtitulo", fontName="Arial", fontSize=12, leading=16, textColor=GRIS, spaceAfter=4),
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=15, leading=19, textColor=AZUL, spaceBefore=14, spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, textColor=colors.black, spaceBefore=9, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=10, leading=14, spaceAfter=6, alignment=TA_LEFT),
    "porque": ParagraphStyle("porque", fontName="Arial", fontSize=10, leading=14, spaceAfter=7, leftIndent=10,
                             borderColor=AZUL, borderWidth=0, backColor=colors.HexColor("#F1F5FB"), borderPadding=6),
    "nota": ParagraphStyle("nota", fontName="Arial-Italic", fontSize=8.5, leading=11, textColor=GRIS, spaceAfter=8),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=8.5, leading=11),
    "celda_b": ParagraphStyle("celda_b", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=colors.white),
    "formula": ParagraphStyle("formula", fontName="Arial", fontSize=10, leading=14, leftIndent=24, spaceAfter=8,
                              textColor=colors.HexColor("#14213D")),
}


def P(texto, estilo="p"):
    return Paragraph(texto, S[estilo])


def porque(texto):
    return P(f"<b>Por qué:</b> {texto}", "porque")


def lista(items, estilo="p"):
    return ListFlowable([ListItem(P(t, estilo), leftIndent=12) for t in items], bulletType="bullet",
                        start="•", leftIndent=14, bulletFontName="Arial")


def tabla(filas, anchos, resaltar=None):
    datos = [[Paragraph(str(c), S["celda_b"] if i == 0 else S["celda"]) for c in fila] for i, fila in enumerate(filas)]
    t = Table(datos, colWidths=[a * cm for a in anchos], repeatRows=1)
    estilo = [("BACKGROUND", (0, 0), (-1, 0), AZUL), ("VALIGN", (0, 0), (-1, -1), "TOP"),
              ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#B8BEC9")),
              ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    for r in resaltar or []:
        estilo.append(("BACKGROUND", (0, r), (-1, r), AZUL_CLARO))
    t.setStyle(TableStyle(estilo))
    return t


def figura(nombre, ancho_cm, pie):
    ruta = RES / "graficos" / nombre
    img = Image(str(ruta))
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

# ---------- portada ----------
h += [Spacer(1, 2.5 * cm),
      P("¿Dónde abrir el próximo Costco en México?", "titulo"),
      P("Metodología del modelo: qué se hizo, cómo se obtuvo, por qué se hizo así y qué quedó fuera", "subtitulo"),
      P("Hugo Cuellar y Valeria Castañeda · Licenciatura en Economía, UAEM · Finanzas Corporativas · noviembre de 2026", "subtitulo"),
      Spacer(1, 1 * cm),
      P("<b>En una frase.</b> Medimos cuánto gastan los hogares en clubes de precio con la ENIGH 2022, estimamos de qué "
        "depende ese gasto con un modelo econométrico, lo llevamos a cada municipio con el Censo 2020, lo comparamos con "
        "los clubes que ya existen (DENUE) y convertimos la demanda que queda sin atender en flujos de efectivo para "
        "calcular VPN y TIR. El resultado: <b>la zona metropolitana de Guadalajara, en su oriente (Tonalá y alrededores), "
        "es la única opción que crea valor de forma robusta</b>, siempre que la tienda cueste menos de unos 48 millones de dólares."),
      Spacer(1, 0.4 * cm),
      P("<b>Cómo leer este documento.</b> Cada paso tiene tres partes: qué hicimos, cómo lo obtuvimos y, en un recuadro "
        "azul, por qué lo hicimos de esa manera y no de otra. La sección 9 enumera lo que no hicimos y la 10 resume "
        "todas las decisiones. Todas las cifras salen de los notebooks <i>01_datos_limpieza</i>, <i>02_modelo_econometrico</i> "
        "y <i>03_evaluacion_financiera</i> de la carpeta <i>proyecto_nuevo</i> del repositorio."),
      Spacer(1, 0.6 * cm),
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
             ["11", "Cómo reproducir el análisis"]], [2, 14]),
      PageBreak()]

# ---------- 1 ----------
h += [P("1. La pregunta y la unidad de análisis", "h1"),
      P("Costco planea 33 aperturas en su año fiscal 2027, una de ellas en México, y tiene una estrategia de expansión "
        "a 20 años en el país. La pregunta del proyecto es en cuál de tres plazas conviene abrirla: Guadalajara, "
        "Monterrey o Querétaro."),
      P("Definimos cada plaza como su <b>zona metropolitana</b> (delimitación de SEDATU, CONAPO e INEGI, <i>Metrópolis de "
        "México 2020</i>): 10 municipios en Guadalajara, 18 en Monterrey y 4 en Querétaro. Dentro de la zona ganadora "
        "bajamos al <b>municipio</b> para sugerir la ubicación."),
      porque("un club de precio atrae compradores de toda la ciudad, no de un solo municipio ni de todo el estado. "
             "Usar el estado completo (por ejemplo, todo Jalisco) mezcla a Guadalajara con municipios rurales que nunca "
             "comprarían en un Costco; usar un solo municipio ignora que la gente de Tonalá puede ir al Costco de Zapopan. "
             "La zona metropolitana es la escala a la que compiten los clubes. El municipio sirve después para elegir el "
             "terreno dentro de ella.")]

# ---------- 2 ----------
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

# ---------- 3 ----------
h += [P("3. La ruta completa en siete pasos", "h1"),
      tabla([["Paso", "Qué se hace", "Herramienta", "Resultado"],
             ["1", "Medir el gasto de cada hogar en clubes de precio", "ENIGH 2022, tabla de gastos", "90,102 hogares; 7,425 compran en clubes"],
             ["2", "Estimar de qué depende ese gasto", "Logit + GLM Gamma + MCO", "Efectos marginales, propensión marginal"],
             ["3", "Calcular la demanda de cada municipio", "Censo 2020 y 2010", "Pesos de demanda por municipio y zona"],
             ["4", "Escalar a ventas reales de la industria", "Costco México, Walmex", "Factor de calibración k = 4.0"],
             ["5", "Medir la oferta actual", "DENUE + aperturas 2026", "38 clubes en las tres zonas"],
             ["6", "Calcular la demanda no atendida y el ingreso marginal", "Modelo de reparto tipo Huff", "Ingreso nuevo para Costco por zona"],
             ["7", "Evaluar el proyecto", "WACC, flujos a 20 años", "VPN, TIR, inversión máxima"]], [1.2, 5.2, 4.3, 5.3]),
      Spacer(1, 0.3 * cm)]

# ---------- 4 ----------
h += [P("4. Datos: fuentes, cómo se obtuvieron y cómo se limpiaron", "h1"),
      tabla([["Fuente", "Qué tomamos", "Cómo se obtuvo"],
             ["INEGI, ENIGH 2022 (nueva serie)", "Gasto por lugar de compra, ingreso, bienes del hogar, factor de expansión",
              "Microdatos ya descargados por el equipo (tablas concentradohogar, hogares y gastoshogar)"],
             ["INEGI, Censo 2020 (ITER)", "Hogares y equipamiento de las viviendas por municipio",
              "Descarga directa de datos abiertos del INEGI, un archivo por estado (14, 19 y 22)"],
             ["INEGI, Censo 2010 (ITER)", "Hogares por municipio en 2010", "Descarga del archivo nacional; nos quedamos con los 3 estados"],
             ["INEGI, DENUE (corte abril 2026)", "Ubicación y tamaño de Costco, Sam's Club y City Club", "Descarga masiva por estado"],
             ["Costco: Annual Report FY2025 y resultados FY2026", "Estados financieros, márgenes por segmento, inversión, almacenes",
              "PDF del portal de inversionistas de Costco"],
             ["Walmart de México, Informe 2025 (BMV)", "Ventas, número de Sam's Club, inflación 2023-2025", "PDF del informe anual"],
             ["Banxico (SIE)", "TIIE 28 días, tasa objetivo, tipo de cambio FIX, inflación", "Consulta de los cuadros CA51, CF373 y CP151 (25-nov-2026)"],
             ["Damodaran (NYU Stern)", "Beta del sector, prima de riesgo de México, tasa del Tesoro", "Tablas de enero y noviembre de 2026"]],
            [4.2, 6.2, 5.6]),
      Spacer(1, 0.2 * cm),
      P("Limpieza (notebook 01)", "h2"),
      lista(["<b>Gasto en clubes.</b> En la tabla <i>gastoshogar</i> cada compra trae su lugar de compra. El código 9 es "
             "\"Tiendas con membresía\". Sumamos el gasto trimestral de ese lugar por hogar y lo multiplicamos por 4 para "
             "tenerlo anual. Los hogares sin compras ahí quedan con gasto cero.",
             "<b>Variables del hogar.</b> Las convertimos en indicadores 0/1: tiene automóvil (auto, camioneta o pickup), "
             "internet, computadora, horno de microondas, lavadora y TV de paga; además el número de integrantes y si vive "
             "en una localidad de 100 mil habitantes o más.",
             "<b>Censo.</b> Tomamos el renglón de total municipal y calculamos la proporción de viviendas con cada bien. "
             "La proporción urbana es la población que vive en localidades de 100 mil habitantes o más.",
             "<b>Clubes.</b> En el DENUE los clubes aparecen como supermercados (SCIAN 462111). Los identificamos por nombre "
             "y exigimos más de 100 empleados para excluir oficinas, CEDIS y gasolineras. Agregamos a mano dos aperturas "
             "que el DENUE aún no registra: Costco Escobedo (mayo de 2026) y Costco Corregidora (diciembre de 2026)."]),
      porque("elegimos solo variables que existen <b>con la misma definición en la ENIGH y en el Censo</b> (\"variables "
             "espejo\"). La ENIGH dice cómo compra un hogar, pero solo es representativa por estado; el Censo cubre todos "
             "los municipios, pero no pregunta por gasto. Si el modelo usara una variable que el Censo no tiene (por "
             "ejemplo, el ingreso exacto), no podríamos aplicarlo a cada municipio. Por eso el ingreso entra en un análisis "
             "aparte (propensión marginal) y no en el modelo que se proyecta.")]

# ---------- 5 ----------
l = logit
filas_logit = [["Variable", "Coeficiente", "Error estándar", "Razón de momios", "Efecto marginal (pp)"]]
for var, r in l.iterrows():
    filas_logit.append([var, f"{r['coeficiente']:.3f}", f"{r['error estándar (cluster upm)']:.3f}",
                        f"{r['razón de momios']:.2f}", f"{r['efecto marginal (puntos %)']:+.1f}"])
filas_gamma = [["Variable", "Coeficiente", "p-valor", "Cambio en el gasto"]]
for var, r in gamma.iterrows():
    filas_gamma.append([var, f"{r['coeficiente']:.3f}", f"{r['p-valor']:.3f}", f"{r['cambio % en gasto']:+.1f}%"])

h += [PageBreak(), P("5. Modelo econométrico de demanda", "h1"),
      P("5.1 Especificación: un modelo de dos partes", "h2"),
      P("El 91.6% de los hogares no compra en clubes y gasta cero; el resto gasta cantidades muy distintas. Por eso "
        "separamos dos decisiones:"),
      P("Parte 1 (¿compra?):  P(compra = 1 | X) = Λ(Xβ), un logit.", "formula"),
      P("Parte 2 (¿cuánto, si compra?):  E[gasto | compra = 1, X] = exp(Xγ), un GLM con distribución Gamma y enlace logarítmico.", "formula"),
      P("Gasto esperado del hogar:  E[gasto | X] = P(compra = 1 | X) × E[gasto | compra = 1, X].", "formula"),
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
             "rutas coinciden: el gasto promedio por estado que predicen tiene una correlación de 0.986 entre ellas."),
      P("5.2 Estimación", "h2"),
      lista(["Todas las regresiones usan el <b>factor de expansión</b> de la ENIGH como ponderador, normalizado a media 1.",
             "Los errores estándar están <b>agrupados por unidad primaria de muestreo</b> (UPM), porque los hogares de una "
             "misma UPM se parecen entre sí y la ENIGH se levanta por conglomerados.",
             "Se estima con los <b>90,102 hogares del país</b>, no solo con los de los tres estados."]),
      porque("con solo los tres estados tendríamos unos 10,000 hogares y menos de 800 compradores; con el país completo hay "
             "7,425 compradores, lo que hace los coeficientes mucho más precisos. Las diferencias propias de cada estado se "
             "revisan después, en la prueba de robustez (escenario B)."),
      P("5.3 Resultados de la parte 1 (logit)", "h2"),
      tabla(filas_logit, [5, 2.6, 2.8, 2.8, 3]),
      P("Todos los coeficientes son significativos al 1%. Efecto marginal = cambio promedio en la probabilidad de comprar, "
        "en puntos porcentuales, si el hogar tiene la característica.", "nota"),
      P("Tener automóvil sube la probabilidad de comprar en clubes en 6.3 puntos, y tener computadora en 5.4. Es coherente "
        "con cómo funciona el formato: compras grandes que requieren coche y hogares de ingreso medio-alto (la computadora "
        "funciona como indicador de ingreso y escolaridad)."),
      P("5.4 Resultados de la parte 2 (GLM Gamma)", "h2"),
      tabla(filas_gamma, [5.5, 3, 3, 4]),
      P("Cambio en el gasto = (e<super>γ</super> − 1) × 100. Internet y tamaño del hogar no son significativos al 5% en esta parte.", "nota"),
      P("5.5 Propensión marginal y elasticidad ingreso", "h2"),
      P("Para responder qué pasa con el gasto en clubes cuando sube el ingreso, estimamos aparte:"),
      lista([f"<b>Propensión marginal a gastar en clubes:</b> {pmg.iloc[0, 3]:.2f} centavos de cada peso adicional de ingreso "
             f"(Jalisco {pmg.iloc[1, 3]:.2f}, Nuevo León {pmg.iloc[2, 3]:.2f}, Querétaro {pmg.iloc[3, 3]:.2f}). Es el coeficiente "
             "de una regresión lineal del gasto en clubes sobre el ingreso anual.",
             "<b>Elasticidad ingreso:</b> 0.65 (error estándar 0.04) entre los hogares que compran. Si el ingreso sube 10%, "
             "su gasto en clubes sube 6.5%: es un bien normal.",
             "<b>Por decil:</b> compra en clubes 1% de los hogares del decil más pobre y 32% del más rico."]),
      figura("02_deciles.png", 15.5, "Participación y gasto en clubes de precio por decil de ingreso. Fuente: ENIGH 2022."),
      P("5.6 Validación", "h2"),
      lista(["<b>AUC de 0.80 dentro de muestra y 0.799 ± 0.004 en validación cruzada de 5 partes.</b> Si se toma al azar un hogar "
             "que compra y uno que no, el modelo da más probabilidad al que compra 8 de cada 10 veces (0.5 sería azar). Que "
             "el valor no baje fuera de muestra indica que el modelo no está sobreajustado.",
             "<b>Pseudo R² de McFadden de 0.16</b>, un valor normal para datos de hogares individuales.",
             "<b>Calibración:</b> por decil de probabilidad predicha, la proporción que realmente compra es muy parecida a la "
             "predicha (gráfica de abajo).",
             "<b>Multicolinealidad:</b> todos los factores de inflación de varianza (VIF) son menores a 1.6.",
             "<b>Heterocedasticidad:</b> la prueba de Breusch-Pagan la detecta (p &lt; 0.001); por eso todos los errores "
             "estándar son robustos y agrupados."]),
      figura("02_calibracion.png", 7.5, "Calibración del logit: cada punto es un decil de probabilidad predicha."),
      ]

# ---------- 6 ----------
h += [PageBreak(), P("6. De hogares a municipios y zonas", "h1"),
      P("La demanda anual de clubes de cada municipio en 2026 se calcula así:"),
      P("Demanda<sub>m,2026</sub> = Hogares<sub>m,2026</sub> × Ĝ<sub>m</sub> × Inflación<sub>2022→2026</sub> × k", "formula"),
      lista(["<b>Ĝ<sub>m</sub></b>: gasto anual esperado por hogar con el perfil del municipio, aplicando el MCO a las proporciones "
             "del Censo 2020.",
             "<b>Hogares 2026</b>: hogares del Censo 2020 proyectados con la tasa de crecimiento anual 2010-2020 de cada municipio.",
             "<b>Inflación 2022→2026</b>: INPC 4.7% (2023), 4.2% (2024), 3.7% (2025) y 3.75% (2026, anual a octubre). "
             "Factor acumulado: 1.174.",
             "<b>k = 4.0</b>: factor de calibración a las ventas reales de la industria."]),
      porque("la ENIGH capta bien <i>quién</i> compra y cómo cambia el gasto entre hogares, pero se queda corta en el "
             "<i>nivel</i>: solo registra compras de hogares (no de negocios con membresía, que son una parte grande de "
             "Costco y Sam's) y los hogares subdeclaran gasto. Expandida al país, la ENIGH da unos 80,400 millones de pesos "
             "de 2025, mientras que Costco México (104,328 millones) más Sam's Club (21.6% de los 1,011,598 millones de "
             "Walmex) vendieron 322,800 millones. Escalamos todo por k = 322,800 / 80,400 ≈ 4.0. Como k es igual para "
             "todas las zonas, <b>no cambia el orden entre ellas</b>: solo pone la demanda en la escala de las ventas reales, "
             "que es la que importa para los flujos. Excluimos City Club porque no publica ventas; eso hace k más pequeño y "
             "la calibración, conservadora."),
      porque("proyectamos hogares con el crecimiento 2010-2020 del INEGI porque las proyecciones municipales de CONAPO no "
             "estaban disponibles para descarga. Para 2026 son solo 6 años de proyección. En la evaluación financiera, a "
             "20 años, usamos un crecimiento más prudente: la mitad del ritmo 2010-2020 en los años 1 a 10 y una cuarta "
             "parte en los años 11 a 20.")]

# ---------- 7 ----------
filas_brecha = [["Zona", "Hogares 2026", "Clubes", "Demanda", "Capacidad actual", "Brecha A", "Brecha B", "Cobertura A / B"]]
for z, r in dzm.iterrows():
    filas_brecha.append([z, fmt(r.hogares_2026), int(r.clubes), fmt(r.demanda_2026), fmt(r.capacidad_2026),
                         f"{r.demanda_no_atendida:+,.0f}", f"{rob.loc[z, 'B · Brecha (millones)']:+,.0f}",
                         f"{r.indice_cobertura:.2f} / {rob.loc[z, 'B · Cobertura']:.2f}"])
h += [P("7. Oferta actual y demanda no atendida", "h1"),
      P("La capacidad de venta de los clubes existentes se calcula con la venta promedio de cada cadena: un Costco en "
        "México vende unos 2,577 millones de pesos al año (104,328 millones entre 42 tiendas, más inflación) y un Sam's "
        "Club unos 1,288 millones (ventas de Sam's entre 176 clubes). City Club no publica cifras; lo tratamos como un Sam's."),
      porque("tratar a City Club como un Sam's probablemente <b>sobreestima</b> la competencia, porque sus clubes son más "
             "pequeños. Preferimos errar hacia el lado conservador: si aun así una zona tiene demanda sin atender, el "
             "resultado es más confiable."),
      tabla(filas_brecha, [2.6, 2.1, 1.4, 1.9, 2.3, 1.8, 1.9, 2.3], resaltar=[1]),
      P("Millones de pesos de 2026, salvo hogares y clubes. Cobertura = capacidad / demanda; menos de 1 indica demanda sin atender.", "nota"),
      P("Dos escenarios: por qué hay un A y un B", "h2"),
      P("El <b>escenario A</b> usa solo el perfil de los hogares. El <b>escenario B</b> agrega un efecto propio de cada estado, "
        "estimado con efectos fijos: los hogares de Querétaro gastan 882 pesos al año más de lo que predice su perfil, y "
        "los de Nuevo León 853 menos."),
      porque("el efecto fijo estatal puede reflejar dos cosas que no podemos separar con estos datos: preferencias "
             "distintas (que sí son demanda) o más o menos oferta cerca (que no lo es: en un estado con pocos clubes se "
             "compra menos aunque se quiera). Como no sabemos cuál pesa más, presentamos los dos escenarios y buscamos una "
             "decisión que funcione en ambos. Guadalajara es la única zona con brecha positiva en los dos."),
      figura("02_brecha_zm.png", 14, "Demanda estimada contra capacidad de los clubes existentes, escenario A."),
      P("Dentro de la zona de Guadalajara, el municipio con más demanda sin club propio es <b>Tonalá</b>: 187,000 hogares, "
        "2,298 millones de pesos de demanda al año y ningún club de precio. Le siguen el propio municipio de Guadalajara y "
        "San Pedro Tlaquepaque. Los tres Costcos actuales están en Zapopan, Tlajomulco y Guadalajara, al poniente y al sur."),
      ]

# ---------- 8 ----------
b = vpn[vpn.capex == "base"].set_index(["escenario", "zona"])
lo = vpn[vpn.capex == "bajo"].set_index(["escenario", "zona"])
filas_vpn = [["Zona, escenario", "Ingreso marginal 2026", "Inversión máxima (mdd)", "VPN con 35 mdd", "TIR con 35 mdd", "VPN con 68 mdd"]]
for (e, z) in [("A", "Guadalajara"), ("B", "Guadalajara"), ("B", "Querétaro"), ("A", "Querétaro"), ("A", "Monterrey"), ("B", "Monterrey")]:
    tir = lo.loc[(e, z), "TIR"]
    filas_vpn.append([f"{z}, {e}", fmt(b.loc[(e, z), "ingreso_marginal_2026_mdp"]), f"{b.loc[(e, z), 'capex_max_mdd']:.1f}",
                      f"{lo.loc[(e, z), 'VPN_mdp']:+,.0f}", "negativa" if pd.isna(tir) or tir < 0 else f"{tir:.1%}",
                      f"{b.loc[(e, z), 'VPN_mdp']:+,.0f}"])
h += [PageBreak(), P("8. Evaluación financiera", "h1"),
      P("8.1 Costo de capital (WACC) en pesos", "h2"),
      P("K<sub>e</sub><super>USD</super> = R<sub>f</sub> + β<sub>L</sub> × ERP<sub>México</sub> = 4.94% + 0.808 × 6.69% = 10.35%", "formula"),
      P("K<sub>e</sub><super>MXN</super> = (1 + K<sub>e</sub><super>USD</super>) × (1 + π<sub>MX</sub>) / (1 + π<sub>EU</sub>) − 1 = 11.43%", "formula"),
      P("La beta desapalancada de supermercados (0.80, Damodaran) se reapalanca con la estructura de Costco (deuda = 1.4% de "
        "su valor de mercado). La deuda cuesta TIIE + 1 punto, 5.29% después de impuestos. Con esos pesos, el "
        "<b>WACC en pesos es 11.34%</b>."),
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
      P("Aquí n es el número de Costcos actuales, w la venta de un Costco promedio y W la capacidad total de clubes. Cada club "
        "se lleva una parte de las ventas proporcional a su tamaño (modelo de reparto tipo Huff con igual accesibilidad)."),
      porque("si ignoráramos la canibalización, Monterrey parecería atractiva porque tiene la mayor demanda total. Pero ahí "
             "35 de cada 100 pesos que vendería la tienda nueva se los quitaría a otros Costcos. El 10-K de Costco reconoce "
             "este riesgo explícitamente. En Guadalajara, en cambio, la tienda atiende demanda que hoy no tiene club."),
      P("8.3 Flujo de efectivo", "h2"),
      tabla([["Concepto", "Supuesto", "Fuente o razón"],
             ["Horizonte", "20 años + valor terminal creciendo al 3%", "Estrategia de Costco en México a 20 años; 3% = inflación meta, sin crecimiento real"],
             ["Margen bruto", "12.03% del ingreso marginal", "Segmento Other International de Costco, FY2025"],
             ["Gastos de operación", "6.83% de la venta de la tienda", "Mismo segmento, sin depreciación"],
             ["Mantenimiento", "0.88% de la venta de la tienda", "Depreciación del segmento"],
             ["Capital de trabajo", "−1.1% de las ventas (entrada de efectivo)", "Costco cobra antes de pagar a proveedores (balance FY2026)"],
             ["Arranque", "80% el año 1, 90% el año 2", "Las tiendas nuevas tardan en madurar (10-K)"],
             ["Inversión", "35.4 a 100.4 mdd; 30% terreno", "Activo fijo neto por almacén y adiciones por apertura del segmento; Escobedo"],
             ["Impuestos", "ISR 30%", "Ley del ISR"]], [3.2, 5.3, 7.5]),
      porque("el margen bruto se aplica al ingreso marginal (la venta realmente nueva), pero los gastos de operación al total "
             "que pasa por las cajas de la tienda, porque el personal, la luz y el mantenimiento dependen del volumen que "
             "atiende el almacén, sea venta nueva o canibalizada. Usamos márgenes del segmento <i>Other International</i> "
             "porque Costco no publica México por separado y ese segmento lo incluye."),
      P("8.4 La regla de decisión: inversión máxima justificable", "h2"),
      P("Costco no publica cuánto invierte por tienda. Por eso, además del VPN con distintos montos, calculamos la "
        "<b>inversión máxima con la que el VPN es cero</b>: el máximo que Costco puede gastar en la tienda sin destruir valor."),
      tabla(filas_vpn, [3.3, 2.7, 2.7, 2.4, 2.4, 2.5], resaltar=[1, 2]),
      P("Millones de pesos salvo donde se indica. Ingreso marginal anual en nivel maduro.", "nota"),
      figura("03_capex_maximo.png", 14, "Inversión máxima justificable por zona y escenario, frente al rango de inversión verificable."),
      porque("reportar un solo VPN dependería de un número (la inversión) que no conocemos. La inversión máxima convierte la "
             "incertidumbre en una regla clara para quien decide: <i>abre en Guadalajara si la tienda cuesta menos de 48 "
             "millones de dólares</i>. Además, el VPN es lineal en la inversión, así que este cálculo es exacto."),
      P("8.5 Sensibilidad", "h2"),
      P(f"Movimos cada supuesto y recalculamos el VPN del escenario B con la inversión base. Lo que más pesa es la demanda "
        f"(±20% mueve el VPN de Guadalajara entre {sens.loc['Demanda −20%', 'Guadalajara']:,.0f} y "
        f"{sens.loc['Demanda +20%', 'Guadalajara']:,.0f} millones) y la inversión. Guadalajara supera a Querétaro en las 12 pruebas; "
        "Monterrey solo sube de lugar con 20% menos demanda, prueba en la que las tres zonas pierden valor."),
      P("8.6 Fuentes de financiamiento", "h2"),
      tabla([["Opción", "Costo antes de impuestos", "Costo después de impuestos", "Riesgo cambiario"]] +
            [[i, f"{r.iloc[0]:.2%}", f"{r.iloc[1]:.2%}", r.iloc[2]] for i, r in fin.iterrows()], [5.5, 3.2, 3.2, 4.1]),
      porque("comparamos el bono en dólares en pesos con la paridad de tasas: pagar en dólares cuesta más en pesos porque se "
             "espera que el peso se deprecie al ritmo del diferencial de inflación. Recomendamos recursos propios porque "
             "Costco tiene 20,207 millones de dólares en caja; el crédito en pesos solo tendría sentido como cobertura "
             "cambiaria, porque calza la moneda de la deuda con la de los ingresos.")]

# ---------- 9 ----------
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
        "la vivienda tiene auto. La ENOE solo es representativa por ciudad y no aporta variables de gasto."),
      ]

# ---------- 10 ----------
h += [P("10. Resumen de decisiones", "h1"),
      tabla([["Decisión", "Alternativa descartada", "Razón"],
             ["Medir demanda con el gasto en \"tiendas con membresía\"", "Usar el ingreso como sustituto", "Mide directamente lo que se quiere predecir"],
             ["Modelo de dos partes", "Una sola regresión lineal", "92% de ceros; dos decisiones distintas"],
             ["Variables espejo ENIGH ↔ Censo", "Incluir el ingreso en el modelo de proyección", "El Censo no mide ingreso; sin espejo no hay proyección municipal"],
             ["MCO lineal para proyectar", "Meter promedios en el logit", "Evita el sesgo de agregación"],
             ["Estimar con todo el país", "Solo los tres estados", "7,425 compradores en lugar de menos de 800"],
             ["Calibrar a ventas reales (k = 4.0)", "Usar el nivel de la ENIGH", "La ENIGH no capta compras de negocios y subdeclara"],
             ["Zona metropolitana como unidad", "Estado o municipio", "Es la escala a la que compiten los clubes"],
             ["Dos escenarios (A y B)", "Elegir uno", "No se puede separar preferencia de oferta"],
             ["Ingreso marginal con canibalización", "Ventas de la tienda", "Lo que importa es la venta nueva para Costco"],
             ["WACC en dólares pasado a pesos", "Bono M directo", "Fuentes verificables y método estándar"],
             ["Inversión máxima como regla", "Un solo VPN", "La inversión por tienda no es pública"],
             ["Corregidora como oferta existente", "Ignorarla", "Abre en diciembre de 2026, antes que la tienda evaluada"]],
            [5, 4.5, 6.5]),
      ]

# ---------- 11 ----------
h += [P("11. Cómo reproducir el análisis", "h1"),
      lista(["Colocar los datos crudos en <i>proyecto_nuevo/data/raw/</i> (ENIGH 2022, Censo 2010 y 2020, DENUE, reportes de "
             "Costco y Walmex), con los nombres que indica el README.",
             "Abrir los notebooks desde la carpeta <i>proyecto_nuevo/notebooks</i> y correrlos en orden: 01, 02 y 03.",
             "Las tablas quedan en <i>resultados/tablas</i>, las gráficas en <i>resultados/graficos</i> y los flujos con fórmulas de "
             "VPN y TIR en <i>resultados/tablas/03_flujos_costco.xlsx</i>.",
             "Este PDF se regenera con <i>python src/generar_pdf_metodologia.py</i>."]),
      Spacer(1, 0.4 * cm),
      P("Fuentes principales: INEGI (ENIGH 2022, Censos de Población y Vivienda 2010 y 2020, DENUE abril 2026); Costco "
        "Wholesale Corporation (Annual Report FY2025 y comunicado de resultados FY2026); Walmart de México (Informe 2025); "
        "Banxico (SIE, 25-nov-2026); A. Damodaran, NYU Stern (enero y noviembre de 2026); Mexico News Daily (2025).", "nota")]

doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                        bottomMargin=2 * cm, title="Metodología del modelo: expansión de Costco en México",
                        author="Hugo Cuellar y Valeria Castañeda")
doc.build(h, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print("PDF generado:", OUT)
