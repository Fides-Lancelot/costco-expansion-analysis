# Análisis de Viabilidad de Expansión de Costco en México

## Objetivo
Determinar la localización espacial óptima de la próxima sucursal de Costco en México mediante un **modelo econométrico de predicción de demanda**, integrado con análisis de oferta y competencia.

## Ciudades analizadas
- **Monterrey**: hub industrial, alto ingreso per cápita
- **Guadalajara**: crecimiento demográfico acelerado, clase media emergente
- **Querétaro**: boom industrial, de las economías de crecimiento más rápido de México

## Materias integradas (5º semestre)
- Finanzas Corporativas
- Econometría
- Contabilidad Social
- Economía Abierta

## Estructura del proyecto
```text
costco-expansion-analysis/
├── data/
│   ├── raw/          # Datos brutos de INEGI (no se incluyen en el repositorio)
│   └── processed/    # Datos limpios listos para análisis
├── notebooks/
│   ├── 01_exploracion_datos.ipynb          # Limpieza de microdatos ENIGH y análisis exploratorio
│   ├── 02_modelo_econometrico_final.ipynb  # Modelo OLS final y pruebas diagnósticas
│   ├── 03_extraccion_denue.ipynb           # Descarga del DENUE y matriz espacial oferta-demanda
│   ├── 03b_inyectar_vehiculos.ipynb        # Agrega parque vehicular (num_auto) desde la ENIGH
│   ├── 04_modelo_logit.ipynb               # Modelo logit de "mercado probado" por municipio
│   └── 05_oferta_demanda_monterrey.ipynb   # Oferta vs. demanda en Nuevo León (en curso)
├── resultados/
│   └── graficos/     # Visualizaciones
└── requirements.txt  # Dependencias de Python
```

Los notebooks usan rutas relativas (`../data/...`, `../resultados/...`), así que deben ejecutarse con la carpeta `notebooks/` como directorio de trabajo.

## Variables clave
- **Demanda:** población, ingreso por hogar, parque vehicular, densidad
- **Oferta y competencia:** clubes de precios existentes, masa de negocios B2B
- **Macroeconómicas:** PIB regional, tasas de interés, inflación
- **Impacto social:** empleo, recaudación fiscal, derrama económica

## Fuentes de datos
- **INEGI (ENIGH 2022 / DENUE):** ingresos por hogar, perfil socioeconómico y densidad de competidores
- **CONAPO:** proyecciones poblacionales a nivel municipal
- **Banco de México:** tasas y crecimiento
- Reportes públicos de Costco

Los datos crudos de la ENIGH deben colocarse en `data/raw/` antes de correr los notebooks 01 y 03b. El notebook 03 descarga el DENUE automáticamente.

## Estado del proyecto
- **Fase 1, completada:** modelo econométrico de demanda (OLS sobre ENIGH), procesamiento de datos y gráficas diagnósticas.
- **Fase 2, en curso:** integración de oferta y competencia (DENUE), modelo logit y análisis por ciudad.

## Autores
**Hugo Cuellar & Valeria Castañeda** | Licenciatura en Economía, Semestre 5
Universidad Autónoma del Estado de Morelos

## Licencia
MIT License
