# Cálculo de Índices Climáticos de Precipitación

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx · raesern@gmail.com  
**Institución:** Departamento de Oceanografía Física, CICESE  
**Última actualización:** Marzo 2026

---

## Descripción general

Script en Python para el cálculo de índices climáticos de extremos de precipitación a partir de datos de reanálisis ERA5-Land. Los índices siguen el estándar internacional de ETCCDI (Expert Team on Climate Change Detection and Indices) y se calculan de forma anual para el período 2000–2024.

---

## Dependencias

| Paquete     | Uso principal                                     |
|-------------|---------------------------------------------------|
| `xarray`    | Lectura y manipulación de datos NetCDF            |
| `icclim`    | Cálculo automatizado de índices climáticos ETCCDI |
| `xclim`     | Funciones auxiliares de calendario y percentiles  |
| `geopandas` | Lectura de geometrías vectoriales (shapefiles)    |
| `shapely`   | Operaciones geométricas                           |
| `numpy`     | Operaciones numéricas                             |

Instalación recomendada con conda:

```bash
conda install -c conda-forge xarray icclim xclim geopandas shapely numpy
```

---

## Estructura de archivos

### Entrada

```
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_pr.nc
```

Archivo NetCDF de precipitación diaria ERA5-Land. La variable de precipitación debe ser la última (o única) variable del dataset. La dimensión temporal puede llamarse `time` o `valid_time` (el script renombra automáticamente).

### Salida

```
C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Precipitacion/
├── PRCPTOT_Era5land.nc
├── rx1day_Era5land.nc
├── r95p_Era5land.nc
├── cdd_Era5land.nc
├── cwd_Era5land.nc
├── r10mm_Era5land.nc
└── r20mm_Era5land.nc
```

Cada archivo NetCDF de salida incluye atributos `definition` y `units`.

---

## Configuración

Al inicio del script se define la región de estudio:

```python
region = 'Yucatan'   # Opciones: 'Nayarit', 'Yucatan', u otra región disponible
```

Los directorios de entrada y salida se construyen dinámicamente a partir de esta variable. **El directorio de salida debe existir antes de ejecutar el script.**

---

## Funciones auxiliares

### `open_ds(dataset)`

Abre un archivo NetCDF y extrae la variable de precipitación.

- **Entrada:** ruta al archivo `.nc`  
- **Salida:** `xarray.DataArray` con la variable de precipitación  
- **Nota:** Renombra automáticamente la dimensión `valid_time` → `time` si es necesario (común en archivos ERA5 descargados desde el CDS de Copernicus)

### `mask(ds)`

Aplica una máscara geográfica basada en el primer paso de tiempo de `pr`. Preserva los píxeles válidos del dominio y asigna `NaN` al resto.

- **Entrada:** `xarray.DataArray`  
- **Salida:** `xarray.DataArray` enmascarado

---

## Índices calculados

### 1. PRCPTOT — Lluvia acumulada anual

> Suma de toda la precipitación en días húmedos (RR ≥ 1 mm) por año.

- **Unidades:** mm  
- **Función:** `icclim.prcptot(pr)`  
- **Salida:** `PRCPTOT_Era5land.nc`

---

### 2. RX1day — Lluvia máxima de un día

> Valor máximo de precipitación diaria registrado en el año.

- **Unidades:** mm  
- **Función:** `icclim.rx1day(pr)`  
- **Salida:** `rx1day_Era5land.nc`

---

### 3. R95p — Precipitación de días muy húmedos

> Suma acumulada anual de la precipitación en días donde RR > percentil 95 de los días húmedos del período completo (2000–2024).

- **Unidades:** mm  
- **Cálculo personalizado:**
  1. Se identifican días húmedos: RR ≥ 1.0 mm
  2. Se calcula el percentil 95 de precipitación sobre todos los días húmedos del período (`RRwn95`)
  3. Por año, se suman las precipitaciones de los días que superan `RRwn95`
- **Salida:** `r95p_Era5land.nc`

```python
wet_days_ref = pr.where(pr >= 1.0)
RRwn95 = wet_days_ref.quantile(0.95, dim='time', skipna=True)
```

---

### 4. CDD — Días consecutivos secos

> Máximo número de días consecutivos con RR < 1 mm en el año.

- **Unidades:** días  
- **Función:** `icclim.cdd(pr)`  
- **Salida:** `cdd_Era5land.nc`

---

### 5. CWD — Días consecutivos húmedos

> Máximo número de días consecutivos con RR ≥ 1 mm en el año.

- **Unidades:** días  
- **Función:** `icclim.cwd(pr)`  
- **Salida:** `cwd_Era5land.nc`

---

### 6. R10mm — Días con lluvia intensa

> Número de días al año con RR ≥ 10 mm.

- **Unidades:** días  
- **Función:** `icclim.r10mm(pr)`  
- **Salida:** `r10mm_Era5land.nc`

---

### 7. R20mm — Días con lluvia muy intensa

> Número de días al año con RR ≥ 20 mm.

- **Unidades:** días  
- **Función:** `icclim.r20mm(pr)`  
- **Salida:** `r20mm_Era5land.nc`

---

## Resumen de índices

| ID      | Nombre                    | Umbral                | Unidades | Fuente        |
|---------|---------------------------|-----------------------|----------|---------------|
| PRCPTOT | Lluvia acumulada          | RR ≥ 1 mm             | mm       | icclim        |
| RX1day  | Lluvia máxima diaria      | —                     | mm       | icclim        |
| R95p    | Días muy húmedos          | RR > p95 días húmedos | mm       | Personalizado |
| CDD     | Días secos consecutivos   | RR < 1 mm             | días     | icclim        |
| CWD     | Días húmedos consecutivos | RR ≥ 1 mm             | días     | icclim        |
| R10mm   | Lluvia intensa            | RR ≥ 10 mm            | días     | icclim        |
| R20mm   | Lluvia muy intensa        | RR ≥ 20 mm            | días     | icclim        |

---

## Notas técnicas

- El umbral de día húmedo es **RR ≥ 1.0 mm** para todos los índices, siguiendo el estándar ETCCDI.
- El percentil 95 para R95p se calcula sobre el **período completo 2000–2024** (período de referencia fijo), no por año.
- La función `mask()` se aplica a todos los índices para asegurar coherencia espacial con el dominio de entrada.
- Los archivos de salida están en formato **NetCDF-4** con metadatos (`definition`, `units`, `name`) embebidos en cada variable.
- Las importaciones de `tg90p` y `tg10p` (índices de temperatura) están presentes en el encabezado pero **no se utilizan** en este script; corresponden a un módulo más amplio del que este archivo forma parte.

---

## Ejecución

```bash
python Calculo_indices_climaticos_lluvia.py
```

Asegurarse de que el directorio de salida exista antes de ejecutar:

```bash
mkdir -p "C:/Users/Ernesto/Downloads/prueba/extremos/Yucatan/Precipitacion/"
```

---

## Referencias

- Sillmann, J. et al. (2013). Climate extremes indices in the CMIP5 multimodel ensemble. *Journal of Geophysical Research: Atmospheres*, 118.  
- [Documentación icclim](https://icclim.readthedocs.io)  
- [Documentación xclim](https://xclim.readthedocs.io)  
- [ERA5-Land — Copernicus Climate Data Store](https://cds.climate.copernicus.eu)

---


