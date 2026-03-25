# Análisis Técnico: Visualización de Trayectorias de Ciclones Tropicales en México

---

## 1. Descripción General

Este script en R tiene como objetivo **descargar, filtrar, clasificar y visualizar** las trayectorias de ciclones tropicales (CT) que han impactado el territorio mexicano entre los años **2000 y 2024**, dividido en dos cuencas:

| Cuenca                     | Región Geográfica                 | Fuente de Datos        |
|----------------------------|-----------------------------------|------------------------|
| Atlántico / Golfo de México| Lat: 18°–23.5°N, Lon: -92°–-85°W  | `IBTrACS.NA.v04r01.nc` |
| Pacífico Oriental          | Lat: 19°–23°N, Lon: -110°–-100°W  | `IBTrACS.EP.v04r01.nc` |

Los resultados se exportan como **imágenes PNG** (mapas por quinquenio), así como archivos **`.Rda`** y **`.csv`** para análisis posterior.

---

## 2. Librerías Utilizadas y su Función

```r
library(ncdf4)          # Lectura de archivos NetCDF (.nc) — formato estándar climatológico
library(ggplot2)        # Motor principal de visualización (mapas y gráficas)
library(gridExtra)      # Composición de múltiples gráficas en una sola figura
library(grid)           # Bajo nivel de control de layout gráfico
library(lubridate)      # Manejo y parsing de fechas (extracción de año/mes)
library(sf)             # Datos espaciales en formato "Simple Features" (vectoriales)
library(maps)           # Mapas base (bordes de países, costas)
library(rnaturalearth)  # Datos geoespaciales de países del mundo
library(rnaturalearthdata) # Dataset complementario para rnaturalearth
```

---

## 3. Carga de Datos Geoespaciales Base

```r

world <- ne_countries(scale = "medium", returnclass = "sf")                                                                                      
shapefile <- read_sf(".../dest22gw/dest22gw.shp")                    

```

- **`world`**: Polígonos de países del mundo en formato `sf` (Simple Features). Se usa como fondo geográfico en todos los mapas.
- **`shapefile`**: Shapefile de los **estados de México** (INEGI `dest22gw`), utilizado para mostrar límites estatales internos con color gris.

---

## 4. Apertura de Archivos NetCDF (IBTrACS)

```r

TC_f  <- nc_open("IBTrACS.NA.v04r01.nc")   # Atlántico Norte
TC_P  <- nc_open("IBTrACS.EP.v04r01.nc")   # Pacífico Este

```

**IBTrACS** (International Best Track Archive for Climate Stewardship) es la base de datos global de ciclones tropicales del NOAA/WMO. Los archivos `.nc` son multidimensionales:

- **Dimensión 1**: Pasos de tiempo por ciclón (máx. 360 observaciones, cada 3 o 6 horas)
- **Dimensión 2**: Número de ciclones en el registro histórico

### Variables Extraídas

| Variable R          | Variable NetCDF          |Descripción                                              |
|---------------------|--------------------------|---------------------------------------------------------|
| `tc_lat` / `tc_lon` | `lat`, `lon`             |Coordenadas geográficas de cada punto de la trayectoria  |
| `tc_name`           | `name`                   | Nombre del ciclón                                       |
| `tc_nature`         |`nature`                  | Tipo de sistema (tropical, extratropical, etc.)         |
| `tc_landfall`       |`landfall`                | Distancia a tierra en cada punto (km); < 100 = landfall |
| `tc_time`           | `iso_time`               | Fecha/hora en formato ISO 8601                          |
| `tc_season`         | `season`                 | Año de la temporada ciclónica                           |
| `tc_cat`            | `usa_sshs`               | Categoría Saffir-Simpson (-4 a 5) según agencia USA     |
| `tc_Presion`        | `wmo_pres`               | Presión mínima (hPa) reportada por WMO                  |
| `tc_wind`           | `wmo_wind`               | Velocidad máxima de viento (nudos) reportada por WMO    |

---

## 5. Flujo de Procesamiento — Cuenca Atlántica

### 5.1 Selección Temporal

```r
tt <- which(tc_season > 1999, arr.ind = TRUE)
```

Obtiene los **índices de columna** (ciclones) cuya temporada es posterior al año 1999. `arr.ind = TRUE` retorna índices en formato matricial, necesario para indexar un array 2D.

### 5.2 Construcción del Data Frame Principal

```r
ALL_imp <- data.frame("lat" = as.vector(tc_lat[, tt]))
```

El array `tc_lat` tiene dimensiones `[360, N_ciclones]`. Al indexar `[, tt]` se seleccionan solo los ciclones post-1999, y `as.vector()` lo "aplana" en un vector lineal de longitud `360 × n_ciclones_seleccionados`.

Las columnas de metadatos se agregan con `rep(..., each = 360)` para que cada ciclón tenga sus 360 filas con el mismo nombre/temporada/categoría:

```r
ALL_imp$name   <- rep(tc_name[tt], each = 360)
ALL_imp$season <- rep(tc_season[tt], each = 360)
```

### 5.3 Clasificación por Categoría (`cat2`)

La variable `usa_sshs` es numérica (-4 a 5). Se convierte a etiquetas descriptivas:

| Valor `usa_sshs` | Etiqueta `cat2`          |
|------------------|--------------------------|
| ≥ 3              | `MH >=3` (Huracán Mayor) |
| 1 ó 2            | `Hurricane < 3`          |
| 0                | `Trop Storm`             |
| -1               | `Trop Depression`        |
| -4               | `Extratropical`          |
| -3               | `wave/low/disturbance`   |

### 5.4 Limpieza de Datos

```r
ALL_imp$name[ALL_imp$name == "NOT_NAMED"] <- NA
ALL_imp$name[ALL_imp$name == "UNNAMED"]   <- NA
ALL_imp <- na.omit(ALL_imp)
```

Se eliminan filas con nombre nulo (ciclones sin nombre oficial) y cualquier fila con `NA` en cualquier columna. Esto también elimina automáticamente los **pasos de tiempo vacíos** al final de cada trayectoria (los 360 slots no siempre están llenos).

### 5.5 División por Quinquenio

```r
decada1_all <- subset(ALL_imp, ALL_imp$season > 1999 & ALL_imp$season < 2005)  # 2000-2004
decada2_all <- subset(ALL_imp, ALL_imp$season > 2004 & ALL_imp$season < 2010)  # 2005-2009
decada3_all <- subset(ALL_imp, ALL_imp$season > 2009 & ALL_imp$season < 2015)  # 2010-2014
decada4_all <- subset(ALL_imp, ALL_imp$season > 2014 & ALL_imp$season < 2020)  # 2015-2019
decada5_all <- subset(ALL_imp, ALL_imp$season > 2019 & ALL_imp$season < 2025)  # 2020-2024
```

> **Nota**: Aunque se llaman "décadas" en el código, en realidad son **quinquenios** de 5 años.

### 5.6 Filtro Espacial y de Landfall (Región de Interés)

```r
a=23.5; b=18; c=-92; d=-85   # Bounding box: Yucatán / Golfo

tt <- which(ALL_imp$lat < a & ALL_imp$lat > b &
            ALL_imp$lon < d & ALL_imp$lon > c &
            ALL_imp$landing < 100)
```

- Se buscan todos los **puntos de trayectoria** dentro del rectángulo definido por las 4 coordenadas.
- `landing < 100`: el punto está a menos de 100 km de tierra (aproximación de landfall).
- Luego se extraen los **nombres únicos** de los ciclones que cumplan la condición y se reconstruyen sus trayectorias completas (no solo los puntos dentro del bounding box):

```r
CT_in   <- unique(ALL_imp$name2[tt])
Atl_all <- ALL_imp[ALL_imp$name2 %in% CT_in, ]
```

### 5.7 Exclusión Manual de Ciclones

```r
Atl_all <- subset(Atl_all, Atl_all$name2 != "ALEX_2022")
Atl_all <- subset(Atl_all, Atl_all$name2 != "HARVEY_2017")
# ... (28 ciclones excluidos en total)
```

Se eliminan manualmente ciclones que, aunque pasaron por la región, **no impactaron México directamente** o llegaron como depresiones tropicales sin relevancia, o que son falsos positivos del filtro espacial (e.g., ciclones del Pacífico que cruzaron al Atlántico).

---

## 6. Generación de Mapas por Quinquenio (Atlántico)

### 6.1 Posicionamiento de Etiquetas Numéricas

Debido a que ggplot2 no tiene un sistema automático de anti-superposición robusto para líneas de trayectoria, las etiquetas se posicionan **manualmente** referenciando índices de fila específicos:

```r
latct1 <- c(decada1_AM$lat[1], decada1_AM$lat[66] - 0.5, ...)
lonct1 <- c(decada1_AM$lon[1] - 0.5, decada1_AM$lon[66], ...)
```

Cada índice apunta a un punto específico de la trayectoria donde se colocará el número identificador del ciclón.

### 6.2 Estructura del Mapa con ggplot2

```r
map_A1 <- ggplot(data = world) +
  geom_sf() +                             # Fondo: contornos de países
  geom_sf(data = shapefile, color='grey') + # Capa: estados de México
  coord_sf(xlim=c(-110,-70), ylim=c(12,30), expand=FALSE) + # Zoom geográfico
  geom_path(data = decada1_AM,
            aes(x=lon, y=lat, group=name2, colour=cat2),
            alpha=1, size=1) +            # Trayectorias coloreadas por categoría
  scale_color_manual(values = Color_CT) + # Paleta personalizada (definida externamente)
  geom_text(data=data.frame(x=lonct1, y=latct1, label=num1),
            aes(x=x, y=y, label=label)) + # Números sobre trayectorias
  geom_text(data=data.frame(x=-108, y=c(18.5,...), label=paste(num1," ",dec1nomb)),
            aes(x=x, y=y, label=label), hjust=0) # Leyenda textual a la izquierda
```

**Capas del mapa (en orden de renderizado):**
1. Polígonos de países del mundo (fondo)
2. Polígonos de estados de México (gris)
3. Trayectorias de ciclones (líneas coloreadas por categoría)
4. Números identificadores sobre las trayectorias
5. Lista de nombres en el margen izquierdo del mapa

### 6.3 Exportación

```r
ggsave(map_A1, file="CT_Yuc_1.png", width=12, height=10, device='png', dpi=200)
```

Se generan 5 archivos PNG (uno por quinquenio) con resolución de 200 DPI.

---

## 7. Flujo de Procesamiento — Cuenca del Pacífico

El proceso es **estructuralmente idéntico** al del Atlántico, con las siguientes diferencias:

| Parámetro | Atlántico | Pacífico |
|-------------------|------------------------|----------------------------------|
| Archivo fuente    | `IBTrACS.NA.v04r01.nc` | `IBTrACS.EP.v04r01.nc`           |
| Bounding box      | 18°–23.5°N, -92°–-85°W | 19°–23°N, -110°–-100°W           |
| Zoom del mapa     | `xlim(-110,-70)`       | `xlim(-120,-100)`                |
| Prefijo de salida | `CT_Yuc_*.png`         | `CT_Nay_*.png`                   |
| Filtro adicional  | ninguno                | `cat > -1` (excluye depresiones) |

### Diferencia clave en el filtro de landfall del Pacífico

```r
ttP2 <- which(ALLP_imp$lat < a & ALLP_imp$lat > b &
              ALLP_imp$lon < d & ALLP_imp$lon > c &
              ALLP_imp$landing < 100 &
              ALLP_imp$cat > -1)          # ← Filtro adicional: mínimo Tormenta Tropical
```

En el Pacífico se excluyen explícitamente las depresiones tropicales (`cat = -1`) para reducir el ruido en la región costera de Nayarit/Jalisco/Sinaloa.

---

## 8. Exportación de Datos Finales

### Recorte fino dentro del bounding box

Después de generar los mapas, se hace un **segundo recorte más estricto** que extrae solo los puntos geográficamente dentro del rectángulo (antes se extraían trayectorias completas):

```r
Atlan_imp <- subset(Atl_all, Atl_all$lat > b & Atl_all$lat < a &
                              Atl_all$lon > c & Atl_all$lon < d)

Pac_imp   <- subset(Pac_all, Pac_all$lat > b & Pac_all$lat < a &
                              Pac_all$lon > c & Pac_all$lon < d)
```

### Guardado

```r
save(Atlan_imp, file = "CT_Yuc.Rda")       # Formato binario R (rápido para recargar)
write.csv(Atlan_imp, "Yuc_2000_2024.csv")  # CSV para uso externo (Python, Excel, etc.)

save(Pac_imp, file = "CT_Nay.Rda")
write.csv(Pac_imp, "Nay_2000_2024.csv")
```

---

## 9. Diagrama del Flujo General

```
Archivos .nc (IBTrACS)
        │
        ▼
  ncvar_get() ──► Variables: lat, lon, name, season, cat, wind, pres, landfall
        │
        ▼
  Filtro temporal (season > 1999)
        │
        ▼
  Construcción data.frame (360 filas por ciclón × N ciclones)
        │
        ▼
  Reclasificación cat → cat2 (etiquetas descriptivas)
        │
        ▼
  na.omit() ─── Elimina unnamed + pasos vacíos
        │
        ├──► Subconjuntos por quinquenio (decada1_all ... decada5_all)
        │           │
        │           └──► Usados para calcular % de impacto (porc1...porc5)
        │
        ▼
  Filtro espacial + landfall (bounding box + landing < 100)
        │
        ▼
  Exclusión manual de ciclones falsos positivos
        │
        ├──► Subconjuntos por quinquenio (decada1 ... decada5)
        │           │
        │           ▼
        │     Mapas ggplot2 (geom_sf + geom_path + geom_text)
        │           │
        │           └──► ggsave() → CT_Yuc_*.png / CT_Nay_*.png
        │
        ▼
  Recorte estricto dentro del bounding box
        │
        ├──► save()      → CT_Yuc.Rda / CT_Nay.Rda
        └──► write.csv() → Yuc_2000_2024.csv / Nay_2000_2024.csv
```

---

## 10. Variables Globales Implícitas

El código referencia `Color_CT` en `scale_color_manual(values = Color_CT)` pero **no la define dentro del script**. Es una paleta de colores que debe estar definida en el entorno global antes de ejecutar este script, probablemente con la estructura:

```r
Color_CT <- c(
  "wave/low/disturbance" = "greenyellow",
  "Trop Depression"      = "green3",
  "Trop Storm"           = "yellow",
  "Hurricane < 3"        = "red",
  "MH >=3"               = "purple",
  "Extratropical"        = "black"
)
```

---

## 11. Archivos de Salida Generados

| Archivo                         |Tipo           | Contenido                                                         |
|---------------------------------|---------------|-------------------------------------------------------------------|
| `CT_Yuc_1.png` a `CT_Yuc_5.png` | PNG (200 DPI) | Mapas Atlántico por quinquenio                                    |
| `CT_Nay_1.png` a `CT_Nay_5.png` | PNG (200 DPI) | Mapas Pacífico por quinquenio                                     |
| `CT_Yuc.Rda`                    | Binario R     | Data frame `Atlan_imp` (puntos dentro del bounding box Atlántico) |
| `CT_Nay.Rda`                    | Binario R     | Data frame `Pac_imp` (puntos dentro del bounding box Pacífico)    |
| `Yuc_2000_2024.csv`             | CSV           | Mismo contenido que `CT_Yuc.Rda` en formato tabular               |
| `Nay_2000_2024.csv`             | CSV           | Mismo contenido que `CT_Nay.Rda` en formato tabular               |

---

## 12. Posibles Mejoras y Notas Técnicas

1. **`Color_CT` no definido en el script**: Se recomienda incluir la definición al inicio del archivo para garantizar reproducibilidad.
2. **Posicionamiento manual de etiquetas**: Los índices hardcodeados (e.g., `lat[66]`, `lat[107]`) son frágiles ante cambios en los datos. Una alternativa robusta sería usar el punto medio o el punto de máxima intensidad de cada trayectoria.
3. **Error potencial en el filtro del Atlántico**:
   ```r
   tt=which(...& ALL_imp<d & ALL_imp>c ...)  # ← Falta $lon
   ```
   Debería ser `ALL_imp$lon < d & ALL_imp$lon > c`. Sin la columna especificada, R compara el data.frame entero, lo que puede producir resultados inesperados.
4. **`landing` en ALLP_imp**: Se usa `rep()` sin especificar `each`, lo que puede producir un reciclado incorrecto si la longitud no coincide exactamente.
5. **Función `g_legend()`**: Se define en el script del Atlántico pero nunca se invoca explícitamente en el código visible; probablemente es un remanente de una versión anterior con leyenda separada.
