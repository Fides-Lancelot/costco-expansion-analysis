"""Genera resultados/Reporte_final_Costco.pdf: el documento de entrega, organizado según la rúbrica.

Secciones 1 a 6 = criterios 1 a 6 de la rúbrica de Finanzas Corporativas. Cada cifra lleva una nota numerada que la
interpreta. Los términos técnicos se definen en el glosario de Metodologia_modelo_Costco.pdf.

Uso (desde la carpeta proyecto_nuevo):  python src/generar_reporte_final.py
Requiere: reportlab y las tablas y gráficas que producen los notebooks 01 a 03.
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
OUT = RES / "Reporte_final_Costco.pdf"

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
    "h1": ParagraphStyle("h1", fontName="Arial-Bold", fontSize=15, leading=19, textColor=AZUL, spaceBefore=12,
                         spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Arial-Bold", fontSize=11.5, leading=15, textColor=colors.black,
                         spaceBefore=9, spaceAfter=3, keepWithNext=1),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=10, leading=14, spaceAfter=6, alignment=TA_LEFT),
    "clave": ParagraphStyle("clave", fontName="Arial", fontSize=10.5, leading=15, spaceAfter=8, leftIndent=8,
                            backColor=colors.HexColor("#F1F5FB"), borderPadding=7),
    "nota": ParagraphStyle("nota", fontName="Arial-Italic", fontSize=8.5, leading=11, textColor=GRIS, spaceAfter=8),
    "fn": ParagraphStyle("fn", fontName="Arial", fontSize=7.8, leading=10, textColor=colors.HexColor("#2D3748"),
                         leftIndent=12, firstLineIndent=-12, spaceAfter=1.5),
    "celda": ParagraphStyle("celda", fontName="Arial", fontSize=8.5, leading=11),
    "celda_b": ParagraphStyle("celda_b", fontName="Arial-Bold", fontSize=8.5, leading=11, textColor=colors.white),
    "formula": ParagraphStyle("formula", fontName="Arial", fontSize=10, leading=14, leftIndent=24, spaceAfter=8,
                              textColor=colors.HexColor("#14213D")),
}

# ---------- notas numeradas (bajo el bloque que las cita) ----------
_contador = [0]
_pendientes = []


def N(texto):
    _contador[0] += 1
    _pendientes.append((_contador[0], texto))
    return f"<super><font color='#1F4E79'>{_contador[0]}</font></super>"


def notas():
    if not _pendientes:
        return []
    bloque = [HRFlowable(width="30%", thickness=0.5, color=GRIS, hAlign="LEFT", spaceBefore=1, spaceAfter=3)]
    bloque += [Paragraph(f"<super>{n}</super> {t}", S["fn"]) for n, t in _pendientes]
    _pendientes.clear()
    return [KeepTogether(bloque), Spacer(1, 6)]


def P(texto, estilo="p"):
    return Paragraph(texto, S[estilo])


def lista(items):
    return ListFlowable([ListItem(P(t), leftIndent=12) for t in items], bulletType="bullet", start="•",
                        leftIndent=14, bulletFontName="Arial")


def tabla(filas, anchos, resaltar=None, derecha_desde=None):
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
    canvas.drawString(2 * cm, 1.2 * cm, "Expansión de Costco en México · Reporte final")
    canvas.drawRightString(letter[0] - 2 * cm, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def fmt(x, d=0):
    s = f"{x:,.{d}f}"
    return s.replace("-", "−")


def pct(x, d=1):
    return fmt(100 * x, d) + "%"


# ---------- datos de los notebooks ----------
T = RES / "tablas"
dzm = pd.read_csv(T / "02_demanda_oferta_zm.csv", index_col=0)
rob = pd.read_csv(T / "02_robustez_escenarios.csv", index_col=0)
mun = pd.read_csv(T / "02_municipios_candidatos.csv")
vpn = pd.read_csv(T / "03_resultados_vpn_tir.csv")
fin = pd.read_csv(T / "03_fuentes_financiamiento.csv", index_col=0)
sens = pd.read_csv(T / "03_sensibilidad.csv", index_col=0)
amort = pd.read_csv(T / "03_amortizacion_credito.csv")
icm = pd.read_csv(T / "03_ingreso_costo_marginal.csv")


def v(esc, zona, capex, col):
    return vpn[(vpn.escenario == esc) & (vpn.zona == zona) & (vpn.capex == capex)][col].iloc[0]


# Parámetros de mercado (notebook 03; Banxico y Damodaran)
FX = 19.704
RF, BETA_U, BETA_L, ERP = 0.0494, 0.80, 0.808, 0.0669
KE_USD = RF + BETA_L * ERP
PI_MX, PI_US = 0.03, 0.02
KE_MXN = (1 + KE_USD) * (1 + PI_MX) / (1 + PI_US) - 1
TIIE, ISR = 0.065549, 0.30
KD = TIIE + 0.01
WACC = 0.1134
CAPEX_MDD = {"bajo": 35.4, "base": 67.9, "alto": 100.4}

tonala = mun[mun.municipio == "Tonalá"].iloc[0]
h = []

# ================= PORTADA =================
h += [Spacer(1, 2.0 * cm),
      P("¿Dónde abrir el próximo Costco en México?", "titulo"),
      P("Guadalajara, Monterrey o Querétaro: evaluación econométrica y financiera de la apertura del año fiscal 2027",
        "subtitulo"),
      P("Reporte final · Hugo Cuellar y Valeria Castañeda · Licenciatura en Economía, UAEM · Finanzas Corporativas · "
        "25 de noviembre de 2026", "subtitulo"),
      Spacer(1, 0.7 * cm),
      P("<b>Recomendación.</b> Abrir la próxima tienda en el <b>oriente de la zona metropolitana de Guadalajara</b> "
        "(Tonalá y sus límites con Tlaquepaque y Guadalajara), con una inversión de <b>hasta 48 millones de dólares</b>, "
        "formato estándar y terreno arrendado, financiada con recursos propios.", "clave"),
      Spacer(1, 0.3 * cm),
      P("<b>Cómo está organizado.</b> Las secciones 1 a 6 siguen, en el mismo orden, los seis criterios de la rúbrica del "
        "proyecto. El anexo A señala en qué parte del documento se cumple cada elemento que pide la rúbrica. Cada cifra "
        "lleva un número pequeño en azul; la nota con ese número, justo debajo del párrafo o la tabla, explica cómo "
        "interpretarla. La explicación detallada del modelo y el glosario de términos están en el documento "
        "complementario <i>Metodologia_modelo_Costco.pdf</i>."),
      P("<b>Unidades.</b> mdp = millones de pesos; mdd = millones de dólares. Salvo que se diga otra cosa, los pesos son "
        "de 2026, las cantidades de dinero son anuales y los porcentajes son tasas anuales. Un punto porcentual (pp) es "
        "la diferencia entre dos porcentajes."),
      Spacer(1, 0.3 * cm),
      tabla([["Sección", "Contenido", "Criterio de la rúbrica"],
             ["1", "Resumen ejecutivo", "1. Resumen ejecutivo"],
             ["2", "Perfil de la empresa: sector, situación financiera, horizonte y necesidad", "2. Perfil de la empresa"],
             ["3", "Tres opciones de inversión, tres fuentes de financiamiento y las instituciones de donde salen los datos",
              "3. Análisis de opciones y fuentes financieras"],
             ["4", "Comparación cuantitativa (valor del dinero en el tiempo, WACC, tipo de cambio, VPN, TIR, anualidades, "
                   "bonos, sensibilidad) y cualitativa", "4. Comparación cualitativa y cuantitativa"],
             ["5", "Conclusiones cuantitativas y no matemáticas", "5. Conclusiones"],
             ["6", "Guion de la presentación ejecutiva y preguntas probables", "6. Presentación ejecutiva"],
             ["A–C", "Lista de verificación contra la rúbrica, supuestos y fuentes", "Todos"]], [1.6, 9.4, 6.0]),
      PageBreak()]

# ================= 1. RESUMEN EJECUTIVO =================
h += [P("1. Resumen ejecutivo", "h1"),
      P("<b>Objetivo.</b> Costco Wholesale planea 33 aperturas en su año fiscal 2027" + N(
          "Plan anunciado en la llamada con analistas del 24 de septiembre de 2026 para el año fiscal que va de "
          "septiembre de 2026 a agosto de 2027. Es una intención de la empresa, no un hecho; incluye reubicaciones.") +
        ", una de ellas en México. El objetivo de este trabajo es decidir en cuál de tres zonas metropolitanas "
        "(Guadalajara, Monterrey o Querétaro) esa tienda crea más valor para el accionista, cuánto se puede invertir en "
        "ella y cómo conviene financiarla."),
      P("<b>Método.</b> (1) Con la ENIGH 2022 del INEGI estimamos un modelo econométrico de quién compra en clubes de "
        "precio y cuánto gasta (90,102 hogares). (2) Con el Censo 2020 llevamos esa demanda a cada municipio y la "
        "comparamos con los 38 clubes que ya operan en las tres zonas (DENUE). (3) Convertimos la demanda que queda sin "
        "atender en flujos de efectivo a 20 años y los descontamos con un costo de capital (WACC) en pesos de 11.34%" + N(
            "Es el rendimiento mínimo anual que la tienda debe dar para compensar a accionistas y acreedores por el uso "
            "de su dinero y el riesgo que corren. Está en pesos y en términos nominales (incluye inflación). Se calcula "
            "en la sección 4.1.") + "."),
      *notas(),
      P("<b>Resultados clave.</b>", "h2"),
      tabla([["Indicador", "Guadalajara", "Querétaro", "Monterrey"],
             ["Demanda sin atender en 2026, mdp (escenario A / B)" + N(
                 "Diferencia entre lo que los hogares de la zona gastarían en clubes de precio en 2026 y lo que pueden "
                 "vender los clubes que ya existen. Positiva = falta oferta; negativa = sobra. A usa solo el perfil de "
                 "los hogares; B añade el efecto propio de cada estado (sección 4.3)."),
              "+4,259 / +2,174", "−734 / +1,932", "−2,496 / −10,298"],
             ["Ingreso marginal para Costco, mdp (A / B)" + N(
                 "Ventas nuevas que gana Costco en total al abrir la tienda, ya descontadas las que la tienda le quita a "
                 "los Costcos que ya hay en la zona (canibalización). Pesos de 2026, primer año maduro."),
              "2,577 / 2,398", "957 / 2,190", "1,416 / 1,009"],
             ["Inversión máxima con VPN = 0, mdd (A / B)" + N(
                 "La inversión más alta con la que el proyecto todavía no destruye valor. Si la tienda cuesta menos que "
                 "esta cifra, conviene; si cuesta más, no. Negativa significa que ni con inversión cero se recuperaría "
                 "el valor: el flujo de operación ya es negativo."),
              "58 / 48", "negativa / 41", "negativa / negativa"],
             ["VPN con inversión de 35 mdd, mdp (A / B)", "+403 / +225", "−1,033 / +107", "−657 / −649"],
             ["TIR con inversión de 35 mdd (A / B)" + N(
                 "Rendimiento anual que da el proyecto sobre lo invertido. Conviene si supera el WACC de 11.34%. "
                 "No se puede calcular (n.d.) cuando los flujos nunca alcanzan a recuperar la inversión."),
              "16.6% / 14.4%", "n.d. / 12.8%", "negativa"],
             ["Lugar en la matriz de decisión (1 = mejor)", "1 en los 10 indicadores", "2.4 en promedio",
              "2.5 en promedio"]],
            [6.4, 3.6, 3.4, 3.6], resaltar=[]),
      *notas(),
      P("<b>Conclusión.</b> Guadalajara es la única zona con demanda sin atender en los dos escenarios y la mejor en "
        "todos los indicadores financieros. La decisión depende tanto del lugar como del monto: con una inversión como la "
        "de Escobedo (unos 100 mdd) ninguna zona crea valor, así que la tienda debe ser de formato estándar. Los factores "
        "no numéricos apuntan en la misma dirección: el director de finanzas de Costco México dijo en octubre de 2025 que "
        "Guadalajara todavía tiene espacio para otra tienda, el oriente de la ciudad no tiene ningún club de precio, y "
        "Monterrey y Querétaro acaban de recibir tiendas nuevas y enfrentan riesgo de abasto de agua."),
      P("<b>Recomendación.</b> Abrir en Tonalá o en sus límites con Tlaquepaque y Guadalajara; inversión de hasta 48 mdd "
        "con terreno arrendado; financiar con recursos propios y, si se quiere cubrir el riesgo cambiario, con un crédito "
        "en pesos a TIIE + 1 punto. Querétaro queda como la siguiente plaza si su alto consumo por hogar se mantiene.",
        "clave"),
      PageBreak()]

# ================= 2. PERFIL =================
h += [P("2. Perfil de la empresa", "h1"),
      P("2.1 Empresa y sector", "h2"),
      P("Costco Wholesale Corporation (Nasdaq: COST) es la mayor cadena de clubes de precio del mundo: 939 almacenes" + N(
          "Total al cierre del año fiscal 2026 (30 de agosto de 2026), según el comunicado de resultados del 24 de "
          "septiembre de 2026. Incluye almacenes en Estados Unidos, Canadá y otros 12 países.") +
        " en 14 países. Su modelo vende un surtido limitado en grandes volúmenes con margen bruto bajo y obtiene buena "
        "parte de su utilidad de las cuotas de membresía. Por eso le importa abrir donde hay muchos hogares de ingreso "
        "medio y alto, con automóvil, que todavía no tienen un club cerca."),
      P("En México el sector de clubes de precio lo forman tres cadenas: Costco (43 almacenes), Sam's Club de Walmart de "
        "México (176 clubes) y City Club de Soriana. En 2025 Costco de México vendió 104,328 mdp y Sam's Club unos "
        "218,500 mdp" + N(
            "La venta de Sam's es una estimación: 21.6% de los ingresos totales de Walmex en 2025 (1,011,598 mdp), "
            "proporción que Walmex reporta para Sam's. La de Costco México viene del ranking Expansión 500. Ambas son "
            "cifras de prensa o de informes que deben verificarse antes de la entrega (anexo C).") +
        "; juntos suman unos 322,800 mdp, así que Costco tiene alrededor de un tercio del mercado. Cada almacén de "
        "Costco México vende en promedio unos 2,400 mdp al año" + N(
            "104,328 mdp entre 43 almacenes. Es un promedio: las tiendas nuevas venden menos y las maduras de ciudades "
            "grandes, más.") + "."),
      *notas(),
      P("2.2 Situación financiera", "h2"),
      P("Costco crece, es muy rentable para su tipo de negocio y tiene más efectivo que deuda. Cifras en millones de "
        "dólares:"),
      tabla([["Concepto", "FY2026", "FY2025", "Cambio"],
             ["Ventas netas", "297,247", "269,912", "+10.1%"],
             ["Cuotas de membresía", "5,907", "5,323", "+11.0%"],
             ["Utilidad de operación", "11,685", "10,383", "+12.5%"],
             ["Utilidad neta", "9,226", "8,099", "+13.9%"],
             ["Efectivo y equivalentes", "20,207", "14,161", "+42.7%"],
             ["Deuda total", "6,162", "5,788", "+6.5%"],
             ["Inversión en activo fijo (capex)", "6,435", "5,498", "+17.0%"]], [7.0, 3.2, 3.2, 3.6]),
      P("Fuente: Costco, comunicado de resultados del cuarto trimestre FY2026, 24 de septiembre de 2026. El año fiscal "
        "FY2026 va del 1 de septiembre de 2025 al 30 de agosto de 2026.", "nota"),
      tabla([["Razón financiera", "FY2026", "Cómo se lee"],
             ["Margen de operación", "3.9%", "De cada 100 dólares vendidos, 3.9 quedan como utilidad de operación"],
             ["Margen neto", "3.1%", "De cada 100 dólares vendidos, 3.1 quedan como utilidad final"],
             ["Membresías / utilidad de operación", "50.6%", "La mitad de la utilidad de operación equivale a las cuotas: el "
                                                             "negocio depende de tener muchos socios"],
             ["Efectivo / deuda total", "3.3 veces", "Podría pagar toda su deuda más de tres veces con su caja"],
             ["Efectivo neto de deuda", "14,045 mdd", "Caja disponible para invertir sin pedir prestado"],
             ["Capex / ventas", "2.2%", "Lo que reinvierte cada año en tiendas y centros de distribución"]],
            [5.0, 2.4, 9.6]),
      P("Cálculo propio con la tabla anterior.", "nota"),
      P("<b>Riesgo crediticio.</b> S&amp;P y Fitch califican a Costco en AA y DBRS Morningstar en AA (low), con perspectiva "
        "estable" + N(
            "AA es la segunda calificación más alta: indica una capacidad muy fuerte de pagar sus deudas. Por eso en la "
            "sección 3 suponemos que Costco puede pedir prestado con un diferencial pequeño sobre la tasa de referencia "
            "(1 punto sobre TIIE en pesos y 0.6 puntos sobre el Tesoro en dólares).") +
        ". Su deuda equivale a 1.4% de su valor de mercado" + N(
            "Proporción de deuda en la estructura de capital medida a valor de mercado (deuda entre deuda más valor de "
            "las acciones), tomada de Damodaran. Es la ponderación que usa el WACC: casi todo el costo de capital es "
            "costo de las acciones.") + "."),
      *notas(),
      P("<b>Rentabilidad del segmento que incluye a México.</b> Costco no publica a México por separado. Su segmento "
        "<i>Other International</i>, que incluye México, tuvo en FY2025 ingresos de 38,266 mdd y un margen de operación "
        "de 4.3% (Annual Report FY2025, nota 11). De ahí tomamos los márgenes del flujo de efectivo: margen bruto de "
        "12.03%, gastos de operación de 6.83% y mantenimiento de 0.88% de las ventas" + N(
            "Margen bruto: lo que queda de cada peso vendido después de pagar la mercancía. Gastos de operación: "
            "sueldos, renta, luz y demás gastos de la tienda. Mantenimiento: inversión necesaria para conservar la "
            "tienda en buen estado. Todos como porcentaje de las ventas.") + "."),
      *notas(),
      P("2.3 Presencia en las tres zonas", "h2"),
      P("Costco opera 9 tiendas en las zonas estudiadas: 3 en Guadalajara (Zapopan, Tlajomulco y Guadalajara, al poniente "
        "y al sur), 4 en Monterrey (incluida Escobedo, abierta en mayo de 2026, con una inversión reportada de unos "
        "100 mdd) y 2 en Querétaro (incluida Corregidora, que abre en diciembre de 2026" + N(
            "Corregidora todavía no abre, pero lo hará antes que la tienda que evaluamos (año fiscal 2027), así que la "
            "contamos como competencia existente. Si no se contara, Querétaro se vería más atractivo de lo que será.") +
        ")."),
      *notas(),
      P("2.4 Horizonte y necesidad a resolver", "h2"),
      P("<b>Necesidad:</b> elegir la plaza mexicana para la apertura del FY2027 y fijar cuánto se puede invertir en ella "
        "sin destruir valor. <b>Horizonte:</b> 20 años, igual que la estrategia de expansión que la dirección de Costco "
        "México ha mencionado para el país, más un valor terminal que crece al 3% anual" + N(
            "El valor terminal resume en una sola cifra los flujos posteriores al año 20, suponiendo que crecen 3% al "
            "año (la meta de inflación de Banxico, es decir, sin crecimiento real). Sin él, el análisis supondría que la "
            "tienda deja de valer al año 20.") +
        ". <b>Por qué este perfil justifica las opciones:</b> como Costco tiene caja de sobra y calificación AA, el "
        "problema no es conseguir dinero sino ponerlo donde rinda más que su costo de capital. Por eso las opciones que "
        "comparamos son proyectos de inversión (las tres plazas) y la pregunta de financiamiento es secundaria: si "
        "conviene usar caja o deuda en pesos para cubrir el riesgo cambiario."),
      *notas()]

# ================= 3. OPCIONES Y FUENTES =================
cap_gdl = dzm.loc["Guadalajara"]
h += [P("3. Análisis de opciones y fuentes financieras", "h1"),
      P("Comparamos tres opciones de inversión reales (un almacén en cada zona metropolitana) y tres fuentes reales de "
        "financiamiento, con datos de siete instituciones."),
      P("3.1 Opciones de inversión", "h2"),
      tabla([["Opción", "Municipios", "Hogares 2020", "Crecimiento anual de hogares 2010-2020", "Clubes de precio hoy",
              "Costco hoy", "Hogares por club"],
             ["1. Almacén en la ZM de Guadalajara", "10", "1,483,691", "3.1%", "13", "3", "140,043"],
             ["2. Almacén en la ZM de Monterrey", "18", "1,522,975", "3.6%", "19", "4", "109,360"],
             ["3. Almacén en la ZM de Querétaro", "4", "447,579", "5.0%", "6", "2", "101,315"]],
            [4.1, 2.1, 2.1, 2.6, 2.0, 1.6, 2.5]),
      P("ZM = zona metropolitana (delimitación SEDATU-CONAPO-INEGI 2020). Fuentes: INEGI, Censos 2010 y 2020; DENUE, "
        "abril de 2026. Hogares por club usa hogares estimados a 2026 y cuenta Costco, Sam's Club y City Club" + N(
            "Es una medida simple de saturación: cuántos hogares hay por cada club de precio. Más hogares por club "
            "sugiere menos competencia. Guadalajara tiene 140 mil hogares por club contra unos 100 a 110 mil en las "
            "otras dos.") + ".", "nota"),
      *notas(),
      P("3.2 Fuentes de financiamiento", "h2"),
      tabla([["Fuente", "Tasa antes de impuestos", "Tasa después de impuestos", "Riesgo cambiario", "Institución que la respalda"],
             ["1. Recursos propios (caja de 20,207 mdd)", pct(fin.iloc[0, 0], 2), pct(fin.iloc[0, 1], 2), "No",
              "Reporte anual de Costco (SEC); Damodaran"],
             ["2. Crédito bancario o certificado bursátil (CEBURE) en pesos, TIIE + 1 punto, 10 años",
              pct(fin.iloc[1, 0], 2), pct(fin.iloc[1, 1], 2), "No", "Banxico (TIIE); CNBV y BMV/BIVA (emisión)"],
             ["3. Bono corporativo en dólares, Tesoro + 0.6 puntos, expresado en pesos", pct(fin.iloc[2, 0], 2),
              pct(fin.iloc[2, 1], 2), "Sí: deuda en dólares, ingresos en pesos", "Calificadoras (AA); Banxico (FIX)"]],
            [5.4, 2.4, 2.4, 3.0, 3.8]),
      P("La tasa de recursos propios es el costo de oportunidad de los accionistas (sección 4.1)" + N(
          "Usar la caja no es gratis: ese dinero podría devolverse a los accionistas o invertirse en otra tienda, y "
          "ellos esperan ganar al menos 11.43% al año en pesos por el riesgo que corren. Es mayor que el costo de la "
          "deuda porque el accionista cobra después que el acreedor.") +
        ". Las tasas de deuda después de impuestos restan el ahorro de ISR de 30% que dan los intereses" + N(
            "Los intereses se deducen de la base del impuesto. Si la tasa es 7.55%, el costo real para la empresa es "
            "7.55% × (1 − 0.30) = 5.29%. El dividendo no se deduce, por eso la tasa de recursos propios no cambia.") +
        ". El bono en dólares se pasa a pesos con la paridad de Fisher (sección 4.2)."),
      *notas(),
      P("3.3 Instituciones y fuentes de información", "h2"),
      tabla([["Institución", "Dato que usamos", "Fecha", "Para qué sirve"],
             ["Banxico (SIE)", "Tasa objetivo 6.25%; TIIE a 28 días 6.5549%; tipo de cambio FIX 19.7040 pesos por "
                               "dólar; inflación anual 3.75%", "25-nov-2026 (inflación: oct-2026)",
              "Costo de la deuda en pesos, conversión de la inversión a pesos, inflación de corto plazo"],
             ["BMV (Walmart de México)", "Informe 2025: 176 Sam's Club; ingresos de 1,011,598 mdp", "2025",
              "Tamaño del sector y competencia"],
             ["CNBV y BMV/BIVA", "Marco de emisión de certificados bursátiles en pesos", "vigente",
              "Fuente de financiamiento 2"],
             ["SEC / reportes anuales de Costco", "Annual Report FY2025 (10-K) y comunicado de resultados FY2026",
              "FY2025 y FY2026", "Situación financiera, márgenes, inversión por almacén"],
             ["Calificadoras (S&amp;P, Fitch, DBRS)", "AA, AA y AA (low), perspectiva estable", "2026",
              "Diferencial de crédito de las fuentes 2 y 3"],
             ["INEGI", "ENIGH 2022; Censos 2010 y 2020; DENUE", "2022, 2010, 2020, abr-2026",
              "Modelo de demanda y oferta de clubes"],
             ["Damodaran (NYU Stern)", "Beta de supermercados 0.80; prima de riesgo de México 6.69%; Tesoro a 10 años "
                                       "4.94%", "ene-2026 y nov-2026", "Costo de capital (CAPM)"]],
            [3.4, 6.2, 2.8, 4.6]),
      P("Todas las cifras pueden verificarse en la fuente citada. Las que tomamos de prensa sin abrir el documento "
        "original se listan en el anexo C.", "nota"),
      PageBreak()]

# ================= 4. COMPARACIÓN =================
h += [P("4. Comparación cualitativa y cuantitativa", "h1"),
      P("Primero fijamos cuánto vale el dinero en el tiempo para Costco (WACC) y cómo se mueve el tipo de cambio. Luego "
        "medimos la demanda de cada zona, la convertimos en flujos de efectivo y los comparamos con VPN, TIR, índice de "
        "rentabilidad, recuperación, anualidades y costo marginal. Al final comparamos las fuentes de financiamiento, la "
        "sensibilidad de los resultados y los factores cualitativos."),
      P("4.1 Valor del dinero en el tiempo: costo de capital", "h2"),
      P("Un peso dentro de un año vale menos que un peso hoy, porque hoy podría invertirse. La tasa que mide esa "
        "diferencia para Costco es su costo promedio ponderado de capital (WACC). La calculamos en tres pasos:"),
      P(f"Costo de las acciones en dólares (CAPM): Ke = Rf + β × prima = 4.94% + 0.808 × 6.69% = <b>{pct(KE_USD, 2)}</b>",
        "formula"),
      P(f"En pesos (paridad de Fisher): (1 + {pct(KE_USD, 2)}) × (1.03 / 1.02) − 1 = <b>{pct(KE_MXN, 2)}</b>", "formula"),
      P(f"WACC = 98.6% × {pct(KE_MXN, 2)} + 1.4% × {pct(KD, 2)} × (1 − 0.30) = <b>11.34%</b>", "formula"),
      P("Rf es la tasa del bono del Tesoro de Estados Unidos a 10 años; la beta de 0.808 es la de supermercados (0.80) "
        "ajustada por la poca deuda de Costco" + N(
            "La beta mide cuánto se mueve el precio de una acción cuando se mueve todo el mercado. Una beta menor que 1 "
            "indica un negocio menos riesgoso que el promedio, como es normal en ventas de alimentos. Se toma la del "
            "sector y no la de Costco sola porque es más estable.") +
        "; la prima de 6.69% es la que exige un inversionista por invertir en acciones en México en lugar de bonos sin "
        "riesgo" + N(
            "Incluye la prima de un mercado maduro como Estados Unidos más la prima por riesgo país de México. Usarla "
            "reconoce que una tienda en México es más riesgosa que una en Estados Unidos.") +
        ". El factor 1.03 / 1.02 pasa la tasa de dólares a pesos según la diferencia de inflación esperada de largo plazo "
        "(metas de Banxico y de la Reserva Federal). <b>Interpretación:</b> cada peso que Costco reciba dentro de 20 años "
        "vale hoy unos 12 centavos" + N(
            "1 / 1.1134^20 = 0.117. Por eso los flujos de los primeros años pesan mucho más en el VPN que los del final "
            "del horizonte.") + "."),
      *notas(),
      P("4.2 Tipo de cambio", "h2"),
      P("La inversión se cotiza en dólares y los ingresos de la tienda son en pesos. Convertimos la inversión con el FIX "
        "del 25 de noviembre de 2026 (19.704 pesos por dólar) y proyectamos el tipo de cambio con la paridad de Fisher: el "
        "peso se deprecia cada año en la diferencia de inflación entre México (3%) y Estados Unidos (2%)" + N(
            "La paridad de poder de compra relativa dice que, a largo plazo, la moneda con más inflación pierde valor en "
            "la misma proporción. No es un pronóstico de corto plazo: el tipo de cambio puede alejarse mucho de esta "
            "trayectoria en un año dado.") + "."),
      tabla([["Concepto", "Hoy", "Año 5", "Año 10", "Año 20"],
             ["Tipo de cambio esperado, pesos por dólar"] +
             [fmt(FX * ((1 + PI_MX) / (1 + PI_US)) ** t, 2) for t in (0, 5, 10, 20)]], [6.6, 2.6, 2.6, 2.6, 2.6]),
      Spacer(1, 4),
      tabla([["Inversión por tienda", "mdd", "mdp", "De dónde sale"],
             ["Baja", "35.4", fmt(v("A", "Guadalajara", "bajo", "capex_mdp")),
              "Activo fijo neto por almacén del segmento Other International (10-K FY2025)"],
             ["Base", "67.9", fmt(v("A", "Guadalajara", "base", "capex_mdp")), "Punto medio entre baja y alta"],
             ["Alta", "100.4", fmt(v("A", "Guadalajara", "alto", "capex_mdp")),
              "Inversión por apertura del segmento en FY2025; similar a Escobedo"]], [3.2, 1.8, 1.8, 10.2]),
      P("Costco no publica cuánto cuesta una tienda; por eso evaluamos un rango y reportamos la inversión máxima "
        "justificable. Esto es más útil para la decisión que suponer un solo número.", "nota"),
      *notas(),
      P("4.3 Demanda de cada zona (modelo econométrico)", "h2"),
      P("Un modelo de dos partes (logit para la probabilidad de comprar y GLM Gamma para el gasto) muestra que comprar en "
        "clubes depende sobre todo de tener automóvil (+6.3 puntos de probabilidad), computadora (+5.4) e internet (+4.4) "
        "y de vivir en una ciudad grande" + N(
            "Efectos marginales promedio del logit ponderado: por ejemplo, tener automóvil sube la probabilidad de "
            "comprar en clubes en 6.3 puntos porcentuales, manteniendo igual lo demás. Son asociaciones estadísticas, "
            "no prueban que comprar un auto haga que el hogar vaya a Costco.") +
        ". La propensión marginal a gastar en clubes es de 1.35 centavos por cada peso adicional de ingreso y la "
        "elasticidad ingreso es 0.65" + N(
            "Propensión marginal: de cada peso adicional de ingreso, el hogar gasta 1.35 centavos más en clubes (1.13 en "
            "Jalisco, 0.73 en Nuevo León, 1.69 en Querétaro). Elasticidad de 0.65: si el ingreso sube 10%, el gasto en "
            "clubes sube 6.5%; es un bien normal, no de lujo.") +
        ". El modelo clasifica bien a los compradores: AUC de 0.80 en validación cruzada" + N(
            "El AUC mide qué tan bien distingue el modelo a quien compra de quien no: 0.5 sería adivinar al azar y 1 "
            "sería perfecto. 0.80 es un buen nivel para datos de hogares.") +
        ". Multiplicamos el gasto esperado por los hogares de cada municipio y calibramos al tamaño real de la industria."),
      *notas(),
      tabla([["Zona", "Demanda 2026 (A)", "Capacidad de los clubes actuales", "Brecha A", "Brecha B",
              "Cobertura A / B" + N(
                  "Capacidad entre demanda. Menos de 1 significa que la demanda supera a la oferta (hay espacio para otra "
                  "tienda); más de 1, que sobra oferta.")],
             ["Guadalajara", "24,871", "20,612", "+4,259", "+2,174", "0.83 / 0.90"],
             ["Monterrey", "27,133", "29,630", "−2,496", "−10,298", "1.09 / 1.53"],
             ["Querétaro", "9,572", "10,307", "−734", "+1,932", "1.08 / 0.84"]],
            [2.8, 2.6, 3.4, 2.0, 2.0, 4.2], resaltar=[1]),
      P("Millones de pesos de 2026. Escenario A: solo perfil de los hogares. Escenario B: agrega el efecto propio de cada "
        "estado (Querétaro +882 pesos por hogar al año, Nuevo León −853, Jalisco −297).", "nota"),
      *notas(),
      figura("02_brecha_zm.png", 13.5, "Demanda contra capacidad instalada por zona metropolitana, 2026. Fuente: "
                                       "estimación propia con ENIGH 2022, Censo 2020 y DENUE abril 2026."),
      P("Dentro de Guadalajara, <b>Tonalá</b> es el municipio con más demanda sin club propio: unos "
        f"{fmt(round(tonala.hogares_2026, -3))} hogares en 2026 y {fmt(tonala.demanda_mdp)} mdp de demanda al año" + N(
            "Hogares estimados a 2026 con el Censo 2020 y la mitad del ritmo de crecimiento 2010-2020 (3.7% anual en "
            "Tonalá). La demanda es el gasto esperado en clubes de todos sus hogares, no la venta que tendría la tienda: "
            "parte de esos hogares seguirá comprando en otros clubes.") + "."),
      *notas(),
      PageBreak()]


def bloque_marginal():
    filas = [["Zona", "Escenario", "Venta de la tienda nueva", "Ingreso marginal para Costco", "Canibalización",
              "Venta nueva por cada peso" + N(
                  "Ingreso marginal entre venta de la tienda. En Guadalajara, al menos 94 centavos de cada peso que "
                  "vende la tienda son venta nueva para Costco; el resto se lo quita a sus propias tiendas.")]]
    datos = [("Guadalajara", "A", 2577, 2577), ("Guadalajara", "B", 2532, 2398), ("Querétaro", "A", 1915, 957),
             ("Querétaro", "B", 2448, 2190), ("Monterrey", "A", 2171, 1416), ("Monterrey", "B", 1547, 1009)]
    for z, e, vt, im in datos:
        filas.append([z, e, fmt(vt), fmt(im), fmt(vt - im), f"{im / vt:.2f}"])
    return [tabla(filas, [2.8, 2.1, 3.0, 3.2, 2.6, 3.3], resaltar=[1, 2]),
            P("Millones de pesos de 2026. Reparto de mercado tipo Huff: cada club se lleva ventas en proporción a su "
              "tamaño.", "nota")]


def bloque_vpn():
    filas = [["Zona, escenario", "VPN 35 mdd", "TIR 35 mdd", "IR 35 mdd" + N(
        "Índice de rentabilidad: valor presente de los flujos entre la inversión. Mayor que 1 significa que cada peso "
        "invertido regresa más de un peso en valor presente. Sirve para comparar proyectos de distinto tamaño."),
              "Recuperación descontada" + N(
                  "Años que tarda la tienda en recuperar la inversión contando el costo del dinero. Más de 20 años o "
                  "nunca indica un proyecto que no se paga dentro del horizonte."),
              "VPN 68 mdd", "Inversión máxima"]]
    orden = [("A", "Guadalajara"), ("B", "Guadalajara"), ("B", "Querétaro"), ("A", "Querétaro"),
             ("A", "Monterrey"), ("B", "Monterrey")]
    for e, z in orden:
        tir = v(e, z, "bajo", "TIR")
        tir_s = "n.d." if pd.isna(tir) else ("negativa" if tir < 0 else pct(tir))
        pb = v(e, z, "bajo", "payback_desc_años")
        pb_s = "no recupera" if pd.isna(pb) else f"{pb:.1f} años"
        cm_ = v(e, z, "bajo", "capex_max_mdd")
        filas.append([f"{z}, {e}", fmt(v(e, z, "bajo", "VPN_mdp")), tir_s, f"{v(e, z, 'bajo', 'IR'):.2f}", pb_s,
                      fmt(v(e, z, "base", "VPN_mdp")), "negativa" if cm_ < 0 else f"{cm_:.0f} mdd"])
    return [tabla(filas, [3.4, 2.0, 2.0, 1.8, 2.8, 2.2, 2.8], resaltar=[1, 2]),
            P("VPN en millones de pesos de 2026, descontado al WACC de 11.34%. Inversión máxima: monto con el que el VPN "
              "es cero.", "nota")]


h += [P("4.4 Ingreso marginal y canibalización", "h2"),
      P("Una tienda nueva le quita ventas a los Costcos que ya existen en la zona. Lo que importa para la decisión no es "
        "cuánto vende la tienda, sino cuánto más vende Costco en total: el ingreso marginal."),
      *bloque_marginal(), *notas(),
      P("4.5 VPN, TIR, índice de rentabilidad y recuperación", "h2"),
      P("El flujo de cada año es: ingreso marginal × margen bruto − gastos de operación − mantenimiento − ISR + "
        "depreciación, durante 20 años, más el valor terminal. La tienda vende 80% de su nivel maduro el año 1 y 90% el "
        "año 2. Descontamos con el WACC:"),
      P("VPN = −Inversión + Σ<sub>t=1..20</sub> FE<sub>t</sub> / (1 + 0.1134)<super>t</super> + VT / (1.1134)"
        "<super>20</super>", "formula"),
      *bloque_vpn(), *notas(),
      figura("03_capex_maximo.png", 13.0, "Inversión máxima justificable (VPN = 0) por zona y escenario, en millones de "
                                          "dólares, contra el rango de inversión por tienda. Fuente: estimación propia."),
      P("<b>Lectura.</b> Con la inversión baja (35 mdd), Guadalajara crea valor en ambos escenarios y Querétaro solo en el "
        "B. Con la inversión base (68 mdd) ninguna zona tiene VPN positivo" + N(
            "Un VPN negativo no significa que la tienda tenga pérdidas contables: puede tener utilidad cada año, pero "
            "no la suficiente para pagar el costo de capital de 11.34% sobre una inversión tan grande.") +
        ": la decisión depende de construir una tienda de formato estándar. Monterrey destruye valor incluso con "
        "inversión cero, porque la tienda canibaliza a las cuatro que ya hay y la zona está sobreofertada."),
      *notas(),
      PageBreak()]

cae = icm[icm.escenario == "B"].set_index("zona")
h += [P("4.6 Anualidades: costo anual equivalente y costo marginal", "h2"),
      P("Para comparar el costo de la inversión con el ingreso de un año, convertimos la inversión base (1,338 mdp) en una "
        "anualidad a 20 años al WACC:"),
      P("CAE = Inversión × r / [1 − (1 + r)<super>−n</super>] = 1,338 × 0.1134 / [1 − 1.1134<super>−20</super>] = "
        "<b>171.8 mdp al año</b>", "formula"),
      P("Así, el costo marginal anual de la tienda es la mercancía, más la operación, más el costo anual equivalente de la "
        "inversión" + N(
            "El costo anual equivalente es el pago fijo anual que, durante 20 años y al 11.34%, tiene el mismo valor "
            "presente que la inversión. Funciona como una renta que la tienda debe pagar cada año por el capital que "
            "usa.") + ". Escenario B, millones de pesos de 2026:"),
      tabla([["Zona", "Ingreso marginal", "Costo de la mercancía", "Costo de operación", "Costo anual de la inversión",
              "Costo marginal total", "Beneficio marginal antes de ISR"]] +
            [[z, fmt(r.ingreso_marginal), fmt(r["costo_mercancía"]), fmt(r["costo_operación"]),
              fmt(r["costo_capital_anualizado (CAE)"], 1), fmt(r.costo_marginal_total), fmt(r.beneficio_marginal_antes_imp)]
             for z, r in cae.loc[["Guadalajara", "Querétaro", "Monterrey"]].iterrows()],
            [2.6, 2.2, 2.4, 2.2, 2.6, 2.4, 2.6], resaltar=[1]),
      P("Con la inversión base, ninguna zona cubre todavía su costo marginal, pero Guadalajara es la que queda más cerca "
        "(−78 mdp al año en B y −60 en A). Es otra forma de ver el mismo resultado del VPN: hay que bajar la inversión.",
        "nota"),
      *notas(),
      P("<b>Anualidad del crédito en pesos.</b> Si la tienda se financiara con un crédito por la inversión base a 10 años "
        "y 7.55%, el pago fijo anual sería de 195.4 mdp. La tabla de amortización muestra cómo cada pago se reparte entre "
        "interés y capital" + N(
            "Al principio la mayor parte del pago es interés, porque el saldo es alto; con los años, cada vez más "
            "del pago reduce la deuda. El escudo fiscal es el ISR que se ahorra al deducir los intereses (30% del "
            "interés).") + ":"),
      tabla([["Año", "Pago", "Interés", "Escudo fiscal", "Amortización", "Saldo"]] +
            [[int(r["año"]), fmt(r.pago, 1), fmt(r["interés"], 1), fmt(r["escudo fiscal"], 1), fmt(r["amortización"], 1),
              fmt(r.saldo, 1)] for _, r in amort.iterrows()], [1.6, 2.6, 2.6, 2.8, 2.8, 2.8]),
      P("Millones de pesos. Monto inicial: 1,337.8 mdp (67.9 mdd al FIX de 19.704).", "nota"),
      *notas(),
      P("4.7 Valuación de bonos", "h2"),
      P("Para la fuente 3 valuamos un bono corporativo en dólares de Costco a 10 años con cupón anual de 5%. Su precio es "
        "el valor presente de los cupones y del principal al rendimiento que exige el mercado:"),
      P("Precio = Σ<sub>t=1..10</sub> 5 / (1 + y)<super>t</super> + 100 / (1 + y)<super>10</super>", "formula"),
      tabla([["Rendimiento exigido (y)", "Precio por cada 100 de valor nominal", "Lectura"],
             ["5.54% (Tesoro 4.94% + 0.6 puntos)", "95.94", "Se vende con descuento: el cupón es menor que lo que pide el "
                                                            "mercado"],
             ["4.54% (si las tasas bajan 1 punto)", "103.63", "Se vende con premio: el cupón es mayor que lo que pide el "
                                                             "mercado"]], [4.6, 4.4, 8.0]),
      P("El costo del bono en pesos es (1.0554) × (1.03 / 1.02) − 1 = 6.57% antes de impuestos y 4.60% después" + N(
          "Se pasa a pesos con la paridad de Fisher porque Costco pagaría en dólares, pero sus ingresos de la tienda "
          "son en pesos. Si el peso se deprecia más de lo que dice la paridad, el costo real del bono sube.") +
        ". La sensibilidad del precio (de 95.94 a 103.63 con un punto de tasa) muestra el riesgo de tasa que asume quien "
        "compra el bono."),
      *notas(),
      P("4.8 Comparación de las fuentes de financiamiento", "h2"),
      tabla([["Criterio", "Recursos propios", "Crédito en pesos", "Bono en dólares"],
             ["Costo después de impuestos", "11.43%", "5.29%", "4.60%"],
             ["Riesgo cambiario", "No", "No", "Sí"],
             ["Disponibilidad", "Inmediata (14,045 mdd de caja neta)", "Requiere trámite bancario o emisión ante CNBV",
              "Requiere emisión en EE. UU."],
             ["Efecto en la calificación AA", "Ninguno", "Mínimo", "Mínimo"],
             ["Uso recomendado", "Fuente principal", "Cobertura natural: deuda y ingresos en pesos",
              "No recomendado para esta tienda"]], [3.8, 4.4, 4.6, 4.2]),
      P("El bono en dólares es el más barato en papel, pero su ventaja de 0.69 puntos sobre el crédito en pesos puede "
        "desaparecer con una depreciación del peso mayor a la esperada. Como Costco tiene caja de sobra, la tienda puede "
        "financiarse con recursos propios; el crédito en pesos se justifica solo como cobertura cambiaria. La decisión de "
        "dónde abrir no cambia con la fuente de financiamiento, porque evaluamos el proyecto con el WACC de la empresa."),
      PageBreak()]

sens_t = sens.copy()
base_b = sens_t.loc["Caso base (B)"]
filas_s = [["Prueba (escenario B, inversión base)", "Guadalajara", "Querétaro", "Monterrey", "¿Guadalajara sigue primero?"]]
for prueba, r in sens_t.iterrows():
    if prueba == "Caso base (B)":
        continue
    primero = r["Guadalajara"] >= max(r["Querétaro"], r["Monterrey"])
    filas_s.append([prueba, fmt(r["Guadalajara"]), fmt(r["Querétaro"]), fmt(r["Monterrey"]), "Sí" if primero else "No"])
filas_s.append(["<b>Caso base (B)</b>", f"<b>{fmt(base_b['Guadalajara'])}</b>", f"<b>{fmt(base_b['Querétaro'])}</b>",
                f"<b>{fmt(base_b['Monterrey'])}</b>", "Sí"])

h += [P("4.9 Sensibilidad", "h2"),
      P("Cambiamos un supuesto a la vez y recalculamos el VPN de cada zona (millones de pesos):"),
      tabla(filas_s, [6.2, 2.6, 2.6, 2.6, 3.0]),
      P("Lo que más mueve el VPN es la inversión y la demanda. Guadalajara queda primera en 10 de las 12 pruebas" + N(
          "Las 12 pruebas son las filas de la tabla, sin contar el caso base. Todas usan la inversión base de 67.9 mdd, "
          "con la que ninguna zona crea valor; por eso casi todos los VPN son negativos. Lo que interesa aquí es el "
          "orden entre zonas y cuánto se mueve cada una.") +
        ". Las dos excepciones son los cambios de demanda: con 20% más demanda, Querétaro (−80) queda por encima de "
        "Guadalajara (−176), porque su escenario B tiene un consumo por hogar alto; con 20% menos, Monterrey (−1,224) "
        "queda por encima de Guadalajara (−1,299). En ambas pruebas las tres zonas tienen VPN negativo con la inversión "
        "base, así que no cambian la recomendación, pero sí confirman que Querétaro es la segunda opción si su demanda "
        "resulta mayor de lo estimado."),
      *notas(),
      P("4.10 Comparación cualitativa", "h2"),
      tabla([["Factor", "Guadalajara", "Querétaro", "Monterrey"],
             ["Señal de la empresa", "El director de finanzas de Costco México dijo en oct-2025 que la ciudad \"still has "
                                     "room for another one\"", "Corregidora abre en dic-2026: plaza recién atendida",
              "Escobedo abrió en may-2026: plaza recién atendida"],
             ["Hueco geográfico", "Oriente sin clubes: Tonalá, 187 mil hogares", "Mercado pequeño (448 mil hogares) con "
                                                                                 "6 clubes", "19 clubes; la más saturada"],
             ["Crecimiento de hogares 2010-2020", "3.1% anual", "5.0% anual (el más alto)", "3.6% anual"],
             ["Nearshoring", "Moderado", "Alto: impulsa empleo y hogares nuevos", "Alto, pero ya lo atiende Escobedo"],
             ["Agua", "No se evaluó con datos", "Estrés hídrico documentado", "Crisis de abasto en 2022"],
             ["Competencia directa (DENUE)", "9 Sam's Club y 1 City Club; en el oriente, Sam's Tlaquepaque y "
                                             "González Gallo", "3 Sam's Club y 1 City Club",
              "10 Sam's Club y 5 City Club"]], [3.4, 4.8, 4.2, 4.6]),
      P("Fuentes: Mexico News Daily (20-oct-2025 y 3-sep-2025); INEGI, Censos 2010 y 2020; DENUE abril 2026. Seguridad "
        "y logística (distancia a centros de distribución) no se evaluaron y quedan como pendientes.", "nota"),
      P("4.11 Matriz de decisión", "h2"),
      tabla([["Indicador (lugar: 1 = mejor)", "Guadalajara", "Querétaro", "Monterrey"],
             ["VPN, A / B", "1 / 1", "3 / 2", "2 / 3"],
             ["TIR, A / B", "1 / 1", "n.d. / 2", "2 / 3"],
             ["Inversión máxima, A / B", "1 / 1", "3 / 2", "2 / 3"],
             ["Ingreso marginal, A / B", "1 / 1", "3 / 2", "2 / 3"],
             ["Menor canibalización, A / B", "1 / 1", "3 / 2", "2 / 3"],
             ["<b>Promedio</b>", "<b>1.0</b>", "<b>2.4</b>", "<b>2.5</b>"]], [6.4, 3.4, 3.4, 3.8], resaltar=[6])]

# ================= 5. CONCLUSIONES =================
h += [P("5. Conclusiones", "h1"),
      P("<b>Costco debe abrir su tienda del FY2027 en el oriente de la zona metropolitana de Guadalajara, con una "
        "inversión de hasta 48 millones de dólares, formato estándar, terreno arrendado y financiamiento con recursos "
        "propios.</b>", "clave"),
      P("5.1 Factores cuantitativos", "h2"),
      lista(["<b>Demanda.</b> Guadalajara es la única zona con demanda sin atender en los dos escenarios: entre 2,174 y "
             "4,259 mdp al año. Monterrey tiene sobreoferta en ambos y Querétaro solo tiene espacio en el escenario B.",
             "<b>Ingreso marginal.</b> Guadalajara genera el mayor ingreso marginal (2,398 a 2,577 mdp) con la menor "
             "canibalización: al menos 94 centavos de cada peso que vende la tienda son venta nueva para Costco.",
             "<b>Valor.</b> Es la única zona con VPN positivo en ambos escenarios con la inversión baja (+225 a +403 mdp; "
             "TIR de 14.4% a 16.6%, por encima del WACC de 11.34%; índice de rentabilidad de 1.32 a 1.58).",
             "<b>Inversión.</b> Justifica la mayor inversión: 48 a 58 mdd. Querétaro llega a 41 mdd solo en B y "
             "Monterrey no justifica ninguna. Con una tienda como Escobedo (100 mdd) ninguna zona crea valor: la "
             "decisión es tanto dónde como cuánto gastar.",
             "<b>Robustez.</b> Guadalajara queda primera en 10 de las 12 pruebas de sensibilidad y en los 10 "
             "indicadores de la matriz de decisión. Las dos excepciones (demanda ±20%) ocurren con VPN negativo para "
             "las tres zonas.",
             "<b>Financiamiento.</b> Recursos propios como fuente principal; crédito en pesos (5.29% después de "
             "impuestos) solo como cobertura cambiaria; no conviene el bono en dólares por el riesgo cambiario."]),
      P("5.2 Factores no matemáticos", "h2"),
      lista(["<b>Respaldo de la empresa.</b> La propia Costco México dijo en octubre de 2025 que Guadalajara tiene espacio "
             "para otra tienda. Monterrey y Querétaro ya recibieron su apertura reciente (Escobedo y Corregidora).",
             "<b>Ubicación.</b> Las 3 tiendas de Guadalajara están al poniente y al sur; el oriente (Tonalá) no tiene "
             "ningún club de precio y sus hogares crecieron 3.7% al año entre 2010 y 2020.",
             "<b>Agua.</b> Monterrey tuvo una crisis de abasto en 2022 y Querétaro tiene estrés hídrico: un riesgo "
             "operativo para una tienda con alimentos frescos y gasolinera.",
             "<b>Nearshoring.</b> Favorece a Monterrey y Querétaro, pero esa demanda nueva ya la están tomando las tiendas "
             "que acaban de abrir allí.",
             "<b>Competencia.</b> En el oriente de Guadalajara el competidor directo es Sam's Club (Tlaquepaque y "
             "González Gallo), no otro Costco."]),
      P("5.3 Riesgos y condiciones de la recomendación", "h2"),
      lista(["La inversión por tienda no es pública. Antes de decidir, Costco debe cotizar terreno y construcción en "
             "Tonalá y confirmar que caben en 48 mdd.",
             "El modelo usa la ENIGH 2022 y una calibración de 4.0 veces al tamaño real de la industria. La calibración "
             "es igual para las tres zonas, así que no cambia el orden, pero sí el nivel del VPN.",
             "Los márgenes son del segmento Other International, no de México por separado.",
             "Seguridad, logística y disponibilidad de terrenos no se evaluaron con datos."]),
      KeepTogether([P("5.4 Siguientes pasos", "h2"),
      lista(["Cotizar terrenos en arrendamiento en Tonalá y en sus límites con Tlaquepaque y Guadalajara.",
             "Si Querétaro mantiene su alto consumo por hogar (escenario B), evaluarlo para la siguiente apertura.",
             "Repetir el modelo con la ENIGH 2024 y con proyecciones municipales de CONAPO cuando estén disponibles."])]),
      PageBreak()]

# ================= 6. PRESENTACIÓN =================
h += [P("6. Presentación ejecutiva", "h1"),
      P("Guion para una exposición de 10 minutos. Si el tiempo asignado es otro, conviene recortar o ampliar la parte 4, "
        "que es la más larga. Cada bloque tiene un solo mensaje, la cifra que lo sostiene y la gráfica que lo acompaña."),
      tabla([["Min.", "Bloque", "Mensaje que debe quedar", "Cifra o gráfica de apoyo"],
             ["0:00–1:00", "Pregunta y respuesta", "Recomendamos abrir en el oriente de Guadalajara, con hasta 48 mdd",
              "Recuadro de recomendación"],
             ["1:00–2:00", "Empresa", "Costco tiene caja de sobra y calificación AA: el reto es dónde invertir, no cómo "
                                      "conseguir dinero", "Ventas 297,247 mdd; caja 20,207 mdd; 43 tiendas en México"],
             ["2:00–3:00", "Opciones y fuentes", "Tres plazas, tres formas de financiar, siete instituciones",
              "Tablas 3.1 y 3.2"],
             ["3:00–4:30", "Demanda", "Solo Guadalajara tiene demanda sin atender en los dos escenarios",
              "Gráfica de brecha por zona"],
             ["4:30–7:00", "Finanzas", "WACC 11.34%; Guadalajara es la única con VPN positivo en A y B; la inversión "
                                       "máxima es 48 a 58 mdd", "Tabla de VPN y gráfica de inversión máxima"],
             ["7:00–8:00", "Financiamiento y riesgo", "Recursos propios; crédito en pesos como cobertura; sensibilidad",
              "Tabla 4.8 y tabla de sensibilidad"],
             ["8:00–9:00", "Factores no numéricos", "La empresa ya dijo que Guadalajara tiene espacio; Tonalá no tiene "
                                                    "clubes; riesgo de agua en las otras dos", "Tabla 4.10"],
             ["9:00–10:00", "Cierre", "Dónde, cuánto y cómo financiar; Querétaro como siguiente plaza",
              "Recuadro de conclusiones"]], [2.0, 2.8, 6.8, 5.4]),
      P("6.1 Preguntas probables y cómo responderlas", "h2"),
      tabla([["Pregunta", "Respuesta corta"],
             ["¿Por qué el VPN es negativo con la inversión base?", "Porque 68 mdd es una tienda grande. Por eso la "
                                                                   "recomendación incluye un tope de inversión: con 35 a "
                                                                   "48 mdd Guadalajara crea valor."],
             ["¿Por qué confiar en la ENIGH si subdeclara gasto?", "La calibramos a las ventas reales de Costco y Sam's. "
                                                                  "El factor es igual para las tres zonas: cambia el nivel, "
                                                                  "no el orden."],
             ["¿Por qué no Monterrey, si es la zona más grande?", "Ya tiene 19 clubes y 4 Costcos; una tienda nueva le "
                                                                 "quitaría ventas a las existentes. Destruye valor aun con "
                                                                 "inversión cero."],
             ["¿Por qué no usar el bono en dólares, si es más barato?", "Los ingresos son en pesos; una depreciación del "
                                                                       "peso borraría la ventaja de 0.69 puntos."],
             ["¿Por qué contar Corregidora si no ha abierto?", "Abre en diciembre de 2026, antes que la tienda evaluada; "
                                                              "ignorarla inflaría la demanda de Querétaro."],
             ["¿Por qué 20 años?", "Es el horizonte de expansión de Costco en México; lo que sigue se captura con el valor "
                                   "terminal al 3%."]], [6.0, 11.0]),
      P("Recomendaciones de forma: una idea por diapositiva, cifras redondeadas, ensayar con reloj y repartir los bloques "
        "entre los dos integrantes.", "nota"),
      PageBreak()]

# ================= ANEXOS =================
h += [P("Anexo A. Lista de verificación contra la rúbrica", "h1"),
      tabla([["Criterio", "Lo que pide el nivel Excelente", "Dónde se cumple"],
             ["1. Resumen ejecutivo", "Objetivos, resultados clave y conclusiones; conciso y profesional",
              "Sección 1: objetivo, método, tabla de resultados, conclusión y recomendación en una página y media"],
             ["2. Perfil de la empresa", "Empresa y sector, situación financiera, horizonte y necesidad a resolver",
              "2.1 empresa y sector; 2.2 estados financieros, razones y calificación; 2.3 presencia; 2.4 horizonte de 20 "
              "años y necesidad"],
             ["3. Opciones y fuentes", "Al menos tres opciones reales y tres fuentes o instituciones reales con datos "
                                       "actualizados y verificables",
              "3.1 tres plazas; 3.2 tres fuentes de financiamiento; 3.3 Banxico, BMV, CNBV, SEC, calificadoras, INEGI y "
              "Damodaran, con fecha"],
             ["4. Comparación", "Valor del dinero en el tiempo, anualidades, bonos, VPN, TIR, tipo de cambio para elegir "
                                "la mejor opción", "4.1 WACC; 4.2 tipo de cambio; 4.5 VPN, TIR, IR y recuperación; 4.6 "
                                                   "anualidades; 4.7 bonos; 4.8 fuentes; 4.9 sensibilidad; 4.10 "
                                                   "cualitativa; 4.11 matriz"],
             ["5. Conclusiones", "Derivadas del análisis, con factores cuantitativos y no matemáticos",
              "5.1 cuantitativos; 5.2 no matemáticos; 5.3 riesgos; 5.4 siguientes pasos"],
             ["6. Presentación", "Profesional, clara, dentro del tiempo y con dominio del tema",
              "Sección 6: guion cronometrado y preguntas probables; depende del ensayo"]], [3.2, 6.0, 7.8]),
      P("Anexo B. Supuestos principales", "h1"),
      tabla([["Supuesto", "Valor", "Por qué"],
             ["Calibración de la ENIGH a ventas reales", "4.0 veces", "La ENIGH solo capta hogares y subdeclara gasto; "
                                                                      "igual para las tres zonas"],
             ["Venta de City Club por club", "Igual a un Sam's", "Sin cifras públicas; sobreestima la competencia "
                                                                 "(conservador)"],
             ["Corregidora", "Abierta", "Abre en dic-2026, antes de la tienda evaluada"],
             ["Crecimiento de hogares", "Mitad del ritmo 2010-2020 (años 1-10), un cuarto (11-20)",
              "No hay proyecciones municipales de CONAPO descargables"],
             ["Márgenes", "Segmento Other International", "Costco no publica México por separado"],
             ["Arranque", "80% el año 1 y 90% el año 2", "Las tiendas nuevas tardan en madurar"],
             ["Terreno", "30% de la inversión, no se deprecia", "El resto se deprecia en línea recta a 20 años"],
             ["Diferencial de crédito", "TIIE + 1; Tesoro + 0.6", "Emisor con calificación AA"],
             ["Inflación de largo plazo", "3% México, 2% EE. UU.", "Metas de Banxico y de la Reserva Federal"],
             ["ISR", "30%", "Tasa corporativa en México"]], [4.6, 5.0, 7.4]),
      P("Anexo C. Fuentes", "h1"),
      lista(["INEGI: ENIGH 2022 (nueva serie), microdatos; Censo de Población y Vivienda 2020 y 2010, ITER; DENUE, corte "
             "abril de 2026.",
             "Costco Wholesale Corporation: Annual Report FY2025 (10-K, SEC) y comunicado de resultados del 4T FY2026 "
             "(24-sep-2026).",
             "Walmart de México (BMV: WALMEX): Resumen financiero del Informe 2025.",
             "Banxico, SIE: tasa objetivo y TIIE (CA51), tipo de cambio FIX (CF373), inflación (CP151), al 25-nov-2026.",
             "A. Damodaran, NYU Stern: betas por sector y primas de riesgo país (ene-2026); bono del Tesoro (nov-2026).",
             "Mexico News Daily: declaraciones del director de finanzas de Costco México (20-oct-2025) e inversión en "
             "Escobedo (3-sep-2025).",
             "<b>Cifras de prensa por verificar antes de la entrega</b> (no se abrió el documento original): ventas de "
             "Costco de México 2025 (Expansión 500), 21.6% de los ingresos de Walmex que vienen de Sam's, calificaciones "
             "de S&amp;P, Fitch y DBRS, y fecha de apertura de Escobedo."]),
      P("Reproducibilidad: los notebooks 01 a 03 de <i>proyecto_nuevo/notebooks</i> generan todas las tablas y gráficas; "
        "<i>resultados/tablas/03_flujos_costco.xlsx</i> contiene los flujos con fórmulas de VPN y TIR; este documento se "
        "genera con <i>python src/generar_reporte_final.py</i>.", "nota")]

assert not _pendientes, "Quedaron notas sin imprimir"
doc = SimpleDocTemplate(str(OUT), pagesize=letter, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                        bottomMargin=2 * cm, title="Reporte final: expansión de Costco en México",
                        author="Hugo Cuellar y Valeria Castañeda")
doc.build(h, onFirstPage=pie_pagina, onLaterPages=pie_pagina)
print(f"PDF generado: {OUT} ({_contador[0]} notas)")
