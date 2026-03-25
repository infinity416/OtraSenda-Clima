# Procesamiento, Recorte y Conversión de Temperatura y Viento ERA5-Land

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx · raesern@gmail.com  
**Institución:** Departamento de Oceanografía Física, CICESE  
**Última actualización:** Febrero 2026

---

## Descripción general

Script de preprocesamiento para datos de temperatura (máxima, mínima y media) y viento (componentes u y v a 10 m) de ERA5-Land. Realiza en secuencia: corrección del nombre de variable, renombrado de la dimensión temporal, conversión de unidades de Kelvin a Celsius (solo para variables de temperatura), y recorte espacial al estado de interés mediante shapefile oficial. Los archivos resultantes son insumo directo para los scripts de cálculo de índices climáticos de temperatura y viento.

---

## Dependencias

| Paquete     | Uso principal                                         |
|-------------|-------------------------------------------------------|
| `xarray`    | Lectura y manipulación de datos NetCDF multichivo     |
| `geopandas` | Lectura del shapefile de estados                      |
| `shapely`   | Geometría para el recorte espacial                    |
| `rioxarray` | Operaciones de recorte con CRS (implícito vía `.rio`) |

Instalación recomendada con conda:

```bash
conda install -c conda-forge xarray geopandas shapely rioxarray
```

---

## Estructura de archivos

### Entrada

```
C:/Users/Ernesto/Downloads/prueba/{region}_2???_{var}.nc          # Archivos ERA5-Land crudos
C:/users/ernesto/Downloads/DI_export_mex/MX_Estados_WGS84_DI8_region.shp  # Shapefile de estados
```

Los archivos de entrada se leen con `open_mfdataset` usando un patrón glob que captura todos los años disponibles para cada variable.

### Salida

```
C:/Users/Ernesto/Documents/prueba/{region}/
├── {region}_2000-2024_tmax.nc
├── {region}_2000-2024_tmin.nc
├── {region}_2000-2024_tmean.nc
├── {region}_2000-2024_u10m.nc
└── {region}_2000-2024_v10m.nc
```

---

## Configuración

```python
variables = ["tmax", "tmin", "tmean", "u10m", "v10m"]
region    = 'Nayarit'    # Opciones: 'Nayarit', 'Yucatan'
```

El script itera sobre todas las variables en secuencia dentro de un mismo bloque `for`. El patrón de búsqueda se construye dinámicamente por variable:

```python
path = f'C:/Users/Ernesto/Downloads/prueba/{region}_2???_{var}.nc'
```

---

## Flujo de procesamiento

### Paso 1 — Lectura multiparchivo y corrección de nombre de variable

ERA5-Land nombra todas las variables de temperatura como `t2m` por defecto, independientemente de si son máximas, mínimas o medias. El script detecta el nombre original y lo reemplaza por el nombre estandarizado del proyecto.

```python
data = xr.open_mfdataset(path)
variable = list(data)[-1]                        # nombre original (ej. 't2m', 'u10', 'v10')
data = data.rename({variable: var})              # renombrar a 'tmax', 'tmin', etc.
data = data.rename({'valid_time': 'time'})       # estandarizar dimensión temporal
```

### Paso 2 — Conversión de unidades (solo temperatura)

Las variables de temperatura en ERA5-Land vienen en Kelvin. Se convierten a Celsius únicamente para `tmax`, `tmin` y `tmean`; las variables de viento (`u10m`, `v10m`) no se modifican.

```python
if variable_corr in ('tmax', 'tmin', 'tmean'):
    data[variable_corr] = data[variable_corr] - 273.15
```

| Variable | Unidad entrada | Unidad salida | Conversión |
|----------|----------------|---------------|------------|
| tmax     | K              | °C            | − 273.15   |
| tmin     | K              | °C            | − 273.15   |
| tmean    | K              | °C            | − 273.15   |
| u10m     | m/s            | m/s           | ninguna    |
| v10m     | m/s            | m/s           | ninguna    |

### Paso 3 — Recorte espacial al estado

Se recorta el dominio usando el shapefile de estados de México filtrado por nombre de estado.

```python
data_region = mask(data[variable_corr], region)
```

La función `mask()` intenta primero dimensiones `x/y` y si falla usa `longitude/latitude`, cubriendo distintos formatos de coordenadas de ERA5.

---

## Función `mask(change, region)`

Realiza el recorte espacial con `rioxarray`.

| Paso | Operación                                                    |
|------|--------------------------------------------------------------|
| 1    | Asigna dimensiones espaciales (`x/y` o `longitude/latitude`) |
| 2    | Escribe el CRS como `EPSG:4326`                              |
| 3    | Lee el shapefile y filtra por estado (`NOMBRE`)              |
| 4    | Recorta con `rio.clip()`                                     |

- **Entrada:** `xarray.DataArray`, nombre de región (`str`)
- **Salida:** `xarray.DataArray` recortado al polígono del estado

---

## Notas técnicas

- A diferencia del script de precipitación, **no se aplica corrección de zona horaria** en este script. Las variables de temperatura y viento de ERA5-Land se procesan directamente en UTC.
- La conversión de Kelvin a Celsius se aplica en el propio `DataArray` antes del recorte, por lo que el archivo de salida ya contiene los valores en °C.
- El script **no filtra por rango temporal** (no hay `.sel(time=slice(...))`); se asume que el patrón glob ya selecciona únicamente los archivos del período 2000–2024.
- El shapefile `MX_Estados_WGS84_DI8_region.shp` debe estar en `EPSG:4326` para ser compatible con el CRS de ERA5-Land.
- La ruta de salida apunta a `C:/Users/Ernesto/Documents/prueba/` mientras que la de entrada viene de `C:/Users/Ernesto/Downloads/prueba/`. Verificar que esta diferencia sea intencional.

---

## Diferencias respecto al script de precipitación

| Aspecto | Este script   | `procesamiento_nombre_recorte_conversion_precip.py`          |
|-------------------------|-------------------------------|------------------------------|
| Variables               | tmax, tmin, tmean, u10m, v10m | pr                           |
| Conversión de unidades  | K → °C (solo temperatura)     | m → mm + desacumulado        |
| Corrección zona horaria | No                            | Sí (UTC → UTC-7)             |
| Filtro temporal         | No (vía glob)                 | Sí (`.sel(time=slice(...))`) |
| Doble `.diff()`         | No                            | Sí (desacumulado ERA5)       |

---

## Ejecución

```bash
python procesamiento_nombre_recorte_conversion.py
```

Verificar que el directorio de salida exista antes de ejecutar:

```bash
mkdir -p "C:/Users/Ernesto/Documents/prueba/Nayarit/"
```

---

## Relación con otros scripts del proyecto

| Script                                      | Variables que consume   |
|---------------------------------------------|-------------------------|
| `Calculo_indices_climaticos_temperatura.py` | `tmax`, `tmin`, `tmean` |
| `Calculo_indices_climaticos_viento.py`      | `u10m`, `v10m`          |

---

## Referencias

- [Documentación ERA5-Land — variables de temperatura y viento](https://confluence.ecmwf.int/display/CKB/ERA5-Land)
- [Documentación rioxarray](https://corteva.github.io/rioxarray)
- [Documentación xarray open_mfdataset](https://docs.xarray.dev/en/stable/generated/xarray.open_mfdataset.html)
- [INEGI — Marco Geoestadístico Nacional](https://www.inegi.org.mx/temas/mg/)
