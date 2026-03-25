# CT_Atlantico_Yucatan.R

Genera mapas y archivos de datos de los ciclones tropicales que impactaron la región de la **Península de Yucatán** (Atlántico / Golfo de México) entre **2000 y 2024**.

---

## Requisitos

### Software
- R (versión 4.0 o superior)
- Los siguientes paquetes de R instalados:

```r
install.packages(c("ncdf4", "ggplot2", "gridExtra", "lubridate",
                   "sf", "maps", "rnaturalearth", "rnaturalearthdata"))
```

### Archivos necesarios antes de correr el script

| Archivo                               | Ubicación esperada                                | Descripción                                    |
|---------------------------------------|---------------------------------------------------|------------------------------------------------|
| `IBTrACS.NA.v04r01.nc`                | `../CT_paper/`                                    | Base de datos IBTrACS — Atlántico Norte (NOAA) |
| `dest22gw.shp` (y archivos asociados) | `/home/olci/Documents/Datos/Shapefiles/dest22gw/` | Shapefile de estados de México (INEGI)         |

> El archivo IBTrACS puede descargarse en: https://www.ncei.noaa.gov/products/international-best-track-archive

---

## Región de análisis

| Parámetro           | Valor                                     |
|---------------------|-------------------------------------------|
| Latitud             | 18°N – 23.5°N                             |
| Longitud            | -92°W – -85°W                             |
| Criterio de impacto | Distancia a tierra < 100 km               |
| Categoría mínima    | Todas (incluyendo depresiones tropicales) |

---

## Cómo correrlo

1. Verificar que los archivos de entrada estén en las rutas indicadas arriba.
2. Abrir el script en RStudio o ejecutar desde terminal:

```bash
Rscript CT_Atlantico_Yucatan.R
```

3. Los archivos de salida se guardarán en:
```
/home/olci/Documents/ManglarIA/
```

---

## Archivos que produce

### Mapas (PNG)

Cinco mapas, uno por quinquenio, con las trayectorias de los ciclones coloreadas por categoría y numeradas con su nombre en el margen.

| Archivo        | Periodo     | Dimensiones         |
|----------------|-------------|---------------------|
| `CT_Yuc_1.png` | 2000 – 2004 | 12 × 10 in, 200 DPI |
| `CT_Yuc_2.png` | 2005 – 2009 | 12 × 10 in, 200 DPI |
| `CT_Yuc_3.png` | 2010 – 2014 | 12 × 10 in, 200 DPI |
| `CT_Yuc_4.png` | 2015 – 2019 | 12 × 10 in, 200 DPI |
| `CT_Yuc_5.png` | 2020 – 2024 | 12 × 10 in, 200 DPI |

### Datos

| Archivo             | Formato   | Contenido                                                                    |
|---------------------|-----------|------------------------------------------------------------------------------|
| `CT_Yuc.Rda`        | Binario R | Data frame `Atlan_imp` con los puntos de trayectoria dentro del bounding box |
| `Yuc_2000_2024.csv` | CSV       | Mismo contenido que `CT_Yuc.Rda`, compatible con Python / Excel              |

### Columnas del CSV / Rda

| Columna      | Descripción                                                        |
|--------------|--------------------------------------------------------------------|
| `lat`, `lon` | Coordenadas del punto de trayectoria                               |
| `name`       | Nombre del ciclón                                                  |
| `name2`      | Nombre + año (ej. `WILMA_2005`)                                    |
| `season`     | Año de la temporada ciclónica                                      |
| `mes`        | Mes del registro                                                   |
| `cat`        | Categoría numérica Saffir-Simpson (-4 a 5)                         |
| `cat2`       | Categoría en texto (`MH >=3`, `Hurricane < 3`, `Trop Storm`, etc.) |
| `presion`    | Presión mínima en hPa (fuente WMO)                                 |                 
| `wind`       | Velocidad máxima de viento en nudos (fuente WMO)                   |
| `landing`    | Distancia a tierra en km en ese punto                              |
| `nature`     | Tipo de sistema meteorológico                                      |
| `time`       | Fecha y hora del registro (ISO 8601)                               |

---

## Colores por categoría en los mapas

| Categoría            |Color              |
|----------------------|-------------------|
| MH >=3               | Morado            |
| Hurricane < 3        | Rojo              |
| Trop Storm           | Amarillo          |
| Trop Depression      | Verde             |
| Extratropical        | Negro             |
| wave/low/disturbance | Verde amarillento |

---

## Ciclones excluidos manualmente

Los siguientes ciclones fueron removidos del análisis porque, aunque cruzaron la región del bounding box, no impactaron directamente México o llegaron en condiciones de depresión tropical sin relevancia:

`ALEX_2022`, `ALBERTO_2000`, `BARBARA_2013`, `BILL_2003`, `CINDY_2005`, `ETA_2020`, `FAY_2002`, `FELIX_2007`, `GAMMA_2005`, `GORDON_2000`, `HANNA_2014`, `HARVEY_2017`, `IRIS_2001`, `KATRINA_1999`, `MATTHEW_2010`, `NADINE_2024`, `NANA_2020`, `OLGA_2007`, `SARA_2024`, `LARRY_2003`, `ARTHUR_2008`, `MARCO_2008`, `ALEX_2010`, `BARRY_2013`, `RICHARD_2010`, `HELENE_2012`, `DANIELLE_2016`, `ALBERTO_2018`

---

## Contacto y mantenimiento

Para agregar una nueva temporada ciclónica, actualizar el archivo `IBTrACS.NA.v04r01.nc` con la versión más reciente disponible en el sitio del NOAA y verificar que los índices de posicionamiento de etiquetas en los mapas sigan siendo válidos para los nuevos datos.
