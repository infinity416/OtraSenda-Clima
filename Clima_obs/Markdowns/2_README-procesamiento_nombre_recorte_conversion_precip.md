# Procesamiento, Recorte y Conversión de Precipitación ERA5-Land

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx · raesern@gmail.com  
**Institución:** Departamento de Oceanografía Física, CICESE  
**Última actualización:** Marzo 2026

---

## Descripción general

Script de preprocesamiento para datos de precipitación ERA5-Land. Realiza cuatro operaciones en secuencia: corrección del nombre de variable, conversión de zona horaria (UTC → UTC-7), conversión de precipitación acumulada horaria a totales diarios en milímetros, y recorte espacial al estado de interés mediante un shapefile oficial. El archivo resultante es el insumo directo para el cálculo de índices climáticos.

---

## Dependencias

| Paquete     | Uso principal                                         |
|-------------|-------------------------------------------------------|
| `xarray`    | Lectura y manipulación de datos NetCDF multichivo     |
| `pandas`    | Conversión y manejo de zonas horarias                 |
| `geopandas` | Lectura del shapefile de estados                      |
| `shapely`   | Geometría para el recorte espacial                    |
| `rioxarray` | Operaciones de recorte con CRS (implícito vía `.rio`) |

Instalación recomendada con conda:

```bash
conda install -c conda-forge xarray pandas geopandas shapely rioxarray
```

---

## Estructura de archivos

### Entrada

```
C:/Users/Ernesto/Downloads/prueba/{region}_????_?.nc       # Archivos ERA5-Land crudos
C:/users/ernesto/Downloads/DI_export_mex/MX_Estados_WGS84_DI8_region.shp  # Shapefile de estados
```

Los archivos de entrada se leen con `open_mfdataset` usando un patrón glob. ERA5-Land entrega la precipitación como acumulado horario en metros (`m`); este script la convierte a milímetros diarios (`mm`).

### Salida

```
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_pr.nc
```

---

## Configuración

```python
variables = ["pr"]        # Variable a procesar
region    = 'Yucatan'     # Opciones: 'Nayarit', 'Yucatan'
```

El patrón de búsqueda de archivos de entrada se construye dinámicamente:

```python
path = f'C:/Users/Ernesto/Downloads/prueba/{region}_????_?.nc'
```

---

## Flujo de procesamiento

### Paso 1 — Lectura multiparchivo y corrección de nombre de variable

ERA5-Land nombra la precipitación internamente como `tp` o similar. El script detecta el nombre real de la variable y lo renombra a `pr` para estandarizar con los demás scripts del proyecto.

```python
data = xr.open_mfdataset(path)
variable = list(data)[-1]
data = data.rename({variable: 'pr'})
data = data.rename({'valid_time': 'time'})
```

### Paso 2 — Corrección de zona horaria (UTC → UTC-7)

Los datos ERA5-Land vienen en UTC. Se convierten a UTC-7 (zona horaria fija, sin ajuste por horario de verano) para alinear con el horario local de las regiones de estudio (Nayarit, Yucatán).

```python
time_utc  = pd.to_datetime(data['time'].values).tz_localize('UTC')
time_utc7 = time_utc.tz_convert('Etc/GMT+7')
time_utc7_naive = time_utc7.tz_localize(None)
data_corr = data.assign_coords(valid_time=time_utc7_naive)
```

> **Nota:** Se usa `'Etc/GMT+7'` (offset fijo) en lugar de una zona horaria con DST. Verificar si esto es apropiado para el período de estudio completo 2000–2024, especialmente para Nayarit que observa horario de verano.

### Paso 3 — Conversión a precipitación diaria en mm

ERA5-Land almacena la precipitación como acumulado continuo en metros. Para obtener totales diarios en mm se aplica la siguiente cadena de operaciones:

```python
data_corr = data_corr.sel(time=slice('2000', '2024'))
data_corr = data_corr.diff(dim='valid_time')          # diferencia horaria → precipitación por hora
data_corr = data_corr.resample(time='1H').ffill()     # relleno hacia adelante a frecuencia horaria
               .diff('valid_time')                    # segunda diferencia para desacumular
data_corr = data_corr.where(data_corr >= 0, 0)        # eliminar negativos por artefactos numéricos
data_corr = data_corr.resample(time='1D').sum()       # suma diaria
data_corr[var] = data_corr[var] * 1000                # conversión m → mm
data_corr[var]['units'] = 'mm'
```

| Operación                        | Propósito                                        |
|----------------------------------|--------------------------------------------------|
| `.diff(dim='valid_time')`        | Convierte acumulado a incremento horario         |
| `.resample('1H').ffill().diff()` | Desacumula a resolución horaria uniforme         |
| `.where(...>= 0, 0)`             | Elimina valores negativos por precisión numérica |
| `.resample('1D').sum()`          | Agrega a totales diarios                         |
| `* 1000`                         | Convierte metros a milímetros                    |

### Paso 4 — Recorte espacial al estado

Se recorta el dominio usando el shapefile de estados de México filtrado por el nombre del estado de interés.

```python
mask = gpd.read_file('.../MX_Estados_WGS84_DI8_region.shp')
mask = mask[mask.NOMBRE == 'Yucatán']   # o 'Nayarit'
change_mask = change.rio.clip(mask.geometry.apply(mapping), mask.crs)
```

La función `mask()` intenta primero dimensiones `x/y` y si falla usa `longitude/latitude`, cubriendo distintos formatos de coordenadas de ERA5.

---

## Función `mask(change, region)`

Realiza el recorte espacial con `rioxarray`.

| Paso | Operación                                                    |
|------|--------------------------------------------------------------|
| 1    | Asigna dimensiones espaciales (`x/y` o `longitude/latitude`) |
| 2    | Escribe el CRS como `EPSG:4326`                              |
| 3    | Lee el shapefile y filtra por estado                         |
| 4    | Recorta con `rio.clip()`                                     |

- **Entrada:** `xarray.DataArray`, nombre de región (`str`)
- **Salida:** `xarray.DataArray` recortado al polígono del estado

---

## Notas técnicas

- El script procesa **una variable a la vez** iterando sobre la lista `variables`. Para procesar temperatura o viento se debe cambiar el contenido de esa lista y ajustar el patrón de búsqueda de archivos.
- La doble aplicación de `.diff()` con resampleo intermedio es necesaria porque ERA5-Land almacena la precipitación como acumulado desde el inicio de la hora de pronóstico, no como tasa instantánea.
- Los valores negativos que aparecen tras el desacumulado son artefactos de precisión numérica en pasos de tiempo donde el acumulado se reinicia; se corrigen a cero con `.where(... >= 0, 0)`.
- El shapefile `MX_Estados_WGS84_DI8_region.shp` debe estar en `EPSG:4326` para ser compatible con el CRS de ERA5-Land.

---

## Ejecución

```bash
python procesamiento_nombre_recorte_conversion_precip.py
```

Verificar que el directorio de salida exista antes de ejecutar:

```bash
mkdir -p "C:/Users/Ernesto/Downloads/prueba/Yucatan/"
```

---

## Relación con otros scripts del proyecto

| Script                                 | Depende de este archivo                        |
|----------------------------------------|------------------------------------------------|
| `Calculo_indices_climaticos_lluvia.py` | ✅ Usa `{region}_2000-2024_pr.nc` como entrada |

---

## Referencias

- [Documentación ERA5-Land — variables de precipitación](https://confluence.ecmwf.int/display/CKB/ERA5-Land)
- [Documentación rioxarray](https://corteva.github.io/rioxarray)
- [Documentación xarray open_mfdataset](https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html)
- [INEGI — Marco Geoestadístico Nacional](https://www.inegi.org.mx/temas/mg/)
