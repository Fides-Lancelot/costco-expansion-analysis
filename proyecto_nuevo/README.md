# Proyecto nuevo: ¿dónde abrir el próximo Costco?

Análisis reconstruido desde cero con fuentes oficiales. Compara las zonas metropolitanas de **Guadalajara, Monterrey y Querétaro** con un modelo econométrico de demanda (ENIGH + Censo) y una evaluación financiera (VPN, TIR, costo de capital). Los archivos del proyecto original se conservan sin cambios.

## Resultado en una línea

**Guadalajara**, en el oriente de la zona metropolitana (Tonalá y sus límites con Tlaquepaque y Guadalajara). Es la única zona donde la demanda de clubes de precio supera a la oferta en los dos escenarios del modelo. Es también la mejor en VPN, TIR e inversión máxima justificable. Abrir crea valor si la tienda cuesta menos de unos **48 a 58 millones de dólares**.

## Cómo correrlo

Abrir los notebooks desde la carpeta `notebooks/` y correrlos en orden. Los datos crudos van en `data/raw/` (no se suben a GitHub; ver la lista abajo).

| Notebook | Qué hace | Salidas principales |
|---|---|---|
| `01_datos_limpieza.ipynb` | Une la ENIGH 2022 (gasto de cada hogar en "tiendas con membresía"), el Censo 2020 y 2010 por municipio, las zonas metropolitanas y el DENUE de clubes | `data/processed/*.csv` |
| `02_modelo_econometrico.ipynb` | Logit + GLM Gamma (modelo de dos partes), MCO agregable, propensión marginal, elasticidad ingreso, validación cruzada, demanda por municipio y zona, prueba de robustez | `resultados/tablas/02_*`, `resultados/graficos/02_*` |
| `03_evaluacion_financiera.ipynb` | WACC en pesos, ingreso marginal con canibalización, flujos a 20 años, VPN, TIR, periodo de recuperación, costo vs. ingreso marginal, sensibilidad, matriz de decisión, fuentes de financiamiento | `resultados/tablas/03_*`, `03_flujos_costco.xlsx` (con fórmulas `VNA`/`TIR`) |

## Hallazgos clave

**Modelo econométrico (90,102 hogares; 7,425 compran en clubes)**
- Comprar en clubes es cosa de hogares de ingreso alto: 1% de los hogares del decil 1 contra 32% del decil 10.
- La elasticidad ingreso del gasto en clubes es 0.65 (bien normal). La propensión marginal es 1.35 centavos por cada peso adicional de ingreso a nivel nacional: 1.13 en Jalisco, 0.73 en Nuevo León y 1.69 en Querétaro.
- Los mayores efectos sobre la probabilidad de comprar son tener automóvil, computadora e internet, y vivir en una ciudad de 100 mil habitantes o más. El modelo distingue bien a quienes compran de quienes no: AUC de 0.80 en validación cruzada de 5 partes (0.5 sería azar) y pseudo R² de McFadden de 0.16.

**Demanda contra oferta, 2026 (millones de pesos)**

| Zona | Brecha A | Cobertura A | Brecha B | Cobertura B | Clubes |
|---|---|---|---|---|---|
| Guadalajara | +4,259 | 0.83 | +2,174 | 0.90 | 13 |
| Monterrey | −2,496 | 1.09 | −10,298 | 1.53 | 19 |
| Querétaro | −734 | 1.08 | +1,932 | 0.84 | 6 |

El escenario A usa solo el perfil de los hogares. El B agrega el efecto propio de cada estado. Una cobertura menor que 1 significa que la demanda supera a la oferta.

**Finanzas (WACC en pesos 11.4%, horizonte de 20 años)**

| Zona | Ingreso marginal 2026 (A / B) | Inversión máxima con VPN = 0 (A / B) | TIR con inversión de 35 mdd (A / B) |
|---|---|---|---|
| Guadalajara | 2,577 / 2,398 mdp | 58 / 48 mdd | 16.6% / 14.4% |
| Querétaro | 957 / 2,190 mdp | negativa / 41 mdd | n.d. / 12.8% |
| Monterrey | 1,416 / 1,009 mdp | negativa en ambos | negativa |

Este hallazgo coincide con una fuente externa: en octubre de 2025 el director de finanzas de Costco México dijo que Guadalajara "still has room for another one" (Mexico News Daily, 20-oct-2025).

## Checklist contra la rúbrica (Finanzas Corporativas, 30 puntos)

Metodología explicada (qué se hizo, cómo y por qué): `resultados/Metodologia_modelo_Costco.pdf`, generado con `python src/generar_pdf_metodologia.py`.

Documento final: https://claude.ai/artifact/CG5PKPgNS4A5dnE1cVsKwd · Presentación (12 diapositivas): https://claude.ai/artifact/1XyRncHhw34xivxe8LCD7H

| # | Criterio | Dónde está |
|---|---|---|
| 1 | Resumen ejecutivo | Documento, primera sección; diapositiva 1 y 12 |
| 2 | Perfil de la empresa | Documento, "Perfil de la empresa" (FY2026, calificaciones, México, horizonte de 20 años, necesidad); diapositiva 2 |
| 3 | Opciones y fuentes | Documento, "Opciones y fuentes financieras": 3 zonas, 3 fuentes de financiamiento, Banxico, BMV, CNBV, SEC, calificadoras, INEGI; diapositiva 10 |
| 4 | Comparación cuantitativa | Documento, "Comparación cuantitativa": WACC, ingreso marginal, VPN, TIR, recuperación, anualidad, bono, tipo de cambio, sensibilidad; diapositivas 6 a 10; Excel con fórmulas |
| 5 | Conclusiones | Documento, "Conclusiones" (cuantitativas y no matemáticas); diapositivas 11 y 12 |
| 6 | Presentación | Diapositivas con notas del orador; falta ensayar tiempos |

Pendiente antes de entregar: verificar las cifras de prensa citadas sin abrir (Expansión 500, 21.6% de Sam's en Walmex, calificaciones).

## Supuestos que conviene defender en la presentación

1. **Inversión por tienda:** no es pública. Se usa un rango verificable (35 a 100 mdd) y se reporta la inversión máxima justificable.
2. **Calibración k = 4.0:** la ENIGH capta solo hogares y subdeclara gasto. Se escala al tamaño real de la industria (Costco México + Sam's 2025). Es igual para las tres zonas, así que no cambia el orden.
3. **Márgenes:** son del segmento *Other International* de Costco, porque Costco no publica México por separado.
4. **Crecimiento de hogares:** a falta de proyecciones municipales de CONAPO, se usa la mitad del ritmo 2010-2020 (INEGI).
5. **Corregidora:** abre en diciembre de 2026. Se cuenta como oferta existente porque estará operando antes de que abra la tienda que evaluamos (año fiscal 2027).

## Datos crudos (`data/raw/`, no versionados)

- `enigh2022/`: concentradohogar, hogares, viviendas y gastoshogar (INEGI, ENIGH 2022 nueva serie)
- `censo2020/iter2020_{14,19,22}.csv`: INEGI, ITER 2020
- `censo2010/iter2010_mun_14_19_22.csv`: INEGI, ITER 2010 (extracto municipal)
- `denue/denue_{14,19,22}.csv`: INEGI, DENUE (corte abril 2026)
- `costco/`: Annual Report FY2025 y comunicado de resultados FY2026
- `walmex/`: Resumen financiero del Informe 2025
