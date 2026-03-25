# CT_Pacifico_Nayarit.R

Genera mapas y archivos de datos de los ciclones tropicales que impactaron la región costera del **Pacífico Mexicano** (Nayarit / Jalisco / Sinaloa) entre **2000 y 2024**.

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

| Archivo                               | Ubicación esperada |                               Descripción |
|---------------------------------------|----------------------------------------------------|----------------------------------------------|
| `IBTrACS.EP.v04r01.nc`                | `../CT_paper/`                                     | Base de datos IBTrACS — Pacífico Este (NOAA) |
| `dest22gw.shp` (y archivos asociados) | `/home/olci/Documents/Datos/Shapefiles/dest22gw/`  | Shapefile de estados de México (INEGI)       |

> El archivo IBTrACS puede descargarse en: https://www.ncei.noaa.gov/products/international-best-track-archive

---

## Región de análisis

| Parámetro           | Valor |
|---------------------|------------------------------------------------------|
| Latitud             | 19°N – 23°N                                          |
| Longitud            | -110°W – -100°W                                      |
| Criterio de impacto | Distancia a tierra < 100 km                          |
| Categoría mínima    | Tormenta Tropical (depresiones tropicales excluidas) |

> **Diferencia respecto al script del Atlántico:** en el Pacífico se excluyen las depresiones tropicales (`cat > -1`) para reducir el ruido en la región costera.

---

## Cómo correrlo

1. Verificar que los archivos de entrada estén en las rutas indicadas arriba.
2. Abrir el script en RStudio o ejecutar desde terminal:

```bash
Rscript CT_Pacifico_Nayarit.R
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
| `CT_Nay_1.png` | 2000 – 2004 | 10 × 11 in, 200 DPI |
| `CT_Nay_2.png` | 2005 – 2009 | 10 × 11 in, 200 DPI |
| `CT_Nay_3.png` | 2010 – 2014 | 10 × 11 in, 200 DPI |
| `CT_Nay_4.png` | 2015 – 2019 | 10 × 11 in, 200 DPI |
| `CT_Nay_5.png` | 2020 – 2024 | 10 × 11 in, 200 DPI |

### Datos

| Archivo             | Formato   | Contenido                                                                  |
|---------------------|-----------|----------------------------------------------------------------------------|
| `CT_Nay.Rda`        | Binario R | Data frame `Pac_imp` con los puntos de trayectoria dentro del bounding box |
| `Nay_2000_2024.csv` | CSV       | Mismo contenido que `CT_Nay.Rda`, compatible con Python / Excel            |

### Columnas del CSV / Rda

| Columna      | Descripción                                                                              |
|--------------|------------------------------------------------------------------------------------------|
| `lat`, `lon` | Coordenadas del punto de trayectoria                                                     |
| `name`       | Nombre del ciclón                                                                        |
| `name2`      | Nombre + año (ej. `PATRICIA_2015`)                                                       |
| `season`     | Año de la temporada ciclónica                                                            |
| `mes`        | Mes del registro                                                                         |
| `cat`        | Categoría numérica Saffir-Simpson (-4 a 5)                                               |
| `cat2`       | Categoría en texto (`MH >=3`, `Hurricane < 3`, `Trop Storm`, etc.)                       |
| `presion`    | Presión mínima en hPa (fuente WMO). Valor `-999` indica dato no disponible               |
| `wind`       | Velocidad máxima de viento en nudos (fuente WMO). Valor `-999` indica dato no disponible |
| `landing`    | Distancia a tierra en km en ese punto                                                    |
| `nature`     | Tipo de sistema meteorológico                                                            |
| `time`       | Fecha y hora del registro (ISO 8601)                                                     |

> **Nota:** A diferencia del Atlántico, en este script los valores faltantes de `presion` y `wind` se reemplazan con `-999` antes de la limpieza, para conservar registros que de otro modo serían eliminados por `na.omit()`.

---

## Colores por categoría en los mapas

| Categoría            | Color             |
|----------------------|-------------------|
| MH >=3               | Morado            |
| Hurricane < 3        | Rojo              |
| Trop Storm           | Amarillo          |
| Trop Depression      | Verde             |
| Extratropical        | Negro             |
| wave/low/disturbance | Verde amarillento |

---

## Ciclones excluidos manualmente

Los siguientes ciclones fueron removidos del análisis porque, aunque cruzaron la región del bounding box, no impactaron directamente la costa o son registros de temporadas anteriores al periodo de estudio que quedaron incluidos por su trayectoria:

`DEBBY_1988`, `DIANA_1990`, `GERT_1993`, `DOLLY_1996`, `LARRY_2003`, `HERMINE_2010`

---

## Contacto y mantenimiento

Para agregar una nueva temporada ciclónica, actualizar el archivo `IBTrACS.EP.v04r01.nc` con la versión más reciente disponible en el sitio del NOAA y verificar que los índices de posicionamiento de etiquetas en los mapas sigan siendo válidos para los nuevos datos.
