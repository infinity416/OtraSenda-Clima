# Cálculo de Índices Climáticos de Viento

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx · raesern@gmail.com  
**Institución:** Departamento de Oceanografía Física, CICESE  
**Última actualización:** Febrero 2026

---

## Descripción general

Script en Python para el cálculo de índices climáticos de extremos de viento a partir de datos de reanálisis ERA5-Land. Los índices caracterizan la intensidad, dirección y frecuencia del viento diario a 10 metros de altura, calculados de forma anual para el período 2000–2024 a partir de las componentes zonal (`u10m`) y meridional (`v10m`).

---

## Dependencias

| Paquete            | Uso principal                                     |
|--------------------|---------------------------------------------------|
| `xarray`           | Lectura, manipulación y resampleo de datos NetCDF |
| `numpy`            | Cálculo de rapidez y dirección del viento         |
| `scipy.stats.mode` | Cálculo de la moda de la rapidez                  |

Instalación recomendada con conda:

```bash
conda install -c conda-forge xarray numpy scipy
```

---

## Estructura de archivos

### Entrada

```
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_u10m.nc
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_v10m.nc
```

Dos archivos NetCDF de ERA5-Land con resolución diaria: componente zonal del viento (`u`) y componente meridional (`v`), ambas a 10 m de altura. La dimensión temporal puede llamarse `time` o `valid_time`.

### Salida

```
C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Viento/
├── RAP_med_Era5land.nc
├── RAP_mod_Era5land.nc
├── RAP90_mod_Era5land.nc
├── Dir_Era5land.nc
└── DVIn90p_Era5land.nc
└── DVIb10p_Era5land.nc
```

Cada archivo NetCDF de salida incluye atributos `definition` y `units`.

---

## Configuración

```python
region = 'Yucatan'   # Opciones: 'Nayarit', 'Yucatan', u otra región disponible
```

Los directorios de entrada y salida se construyen dinámicamente. **El directorio de salida debe existir previamente.**

---

## Funciones auxiliares

### `open_ds(dataset)`

Abre un archivo NetCDF y extrae la variable principal.

- **Entrada:** ruta al archivo `.nc`
- **Salida:** `xarray.DataArray` con la variable de viento
- **Nota:** Renombra automáticamente `valid_time` → `time` cuando es necesario (ERA5 descargado desde el CDS de Copernicus)

### `mask(ds)`

Aplica una máscara geográfica usando el primer paso de tiempo de `u`. Asigna `NaN` fuera del dominio regional de interés, evitando que píxeles exteriores aparezcan con valor `0` en los índices de frecuencia.

- **Entrada:** `xarray.DataArray`
- **Salida:** `xarray.DataArray` enmascarado

### `calcular_moda(x, axis)`

Calcula la moda de un array usando `scipy.stats.mode`, omitiendo valores `NaN`. Se usa como función de reducción dentro de `resample().reduce()`.

### `calculate_R90p(year_data)`

Para un año dado, calcula el percentil 90 de la rapidez y devuelve la media de los valores que lo superan.

### `DVIn(dataarray, q=0.90)`

Cuenta por año el número de días donde la rapidez supera el percentil 90 del período completo.

### `DVDb(dataarray, q=0.10)`

Cuenta por año el número de días donde la rapidez es inferior al percentil 10 del período completo.

---

## Variable derivada: Rapidez del viento

Todos los índices se calculan sobre la rapidez escalar del viento `RAP`, derivada de las componentes u y v:

```python
RAP = np.sqrt(u**2 + v**2)
```

---

## Índices calculados

### 1. RAP_med — Rapidez media anual

> Promedio anual de la rapidez escalar del viento.

- **Operación:** `RAP.resample(time='YE').mean()`
- **Unidades:** m/s
- **Salida:** `RAP_med_Era5land.nc`

---

### 2. RAP_mod — Moda de la rapidez anual

> Valor de rapidez más frecuente en el año (moda estadística).

- **Operación:** `RAP.resample(time='YE').reduce(calcular_moda, dim='time')`
- **Unidades:** m/s
- **Máscara aplicada:** sí
- **Salida:** `RAP_mod_Era5land.nc`

```python
def calcular_moda(x, axis):
    moda = mode(x, axis=axis, nan_policy='omit')
    return moda.mode
```

---

### 3. RAP90p — Vientos intensos

> Media anual de la rapidez en los días que superan el percentil 90 **del año en curso** (percentil calculado año a año).

- **Operación:** Por año: se calcula p90 anual → se filtran días con RAP > p90 → se promedia
- **Unidades:** m/s
- **Máscara aplicada:** sí
- **Salida:** `RAP90_mod_Era5land.nc`

> **Nota metodológica:** El percentil de referencia para RAP90p se recalcula dentro de cada año individualmente, a diferencia de DVIn90p (índice 6) donde el percentil se calcula sobre el **período completo**. Esta distinción es intencional y responde a objetivos distintos: RAP90p mide la intensidad relativa dentro del año; DVIn90p mide la frecuencia respecto a un umbral histórico fijo.

---

### 4. Dir — Dirección dominante del viento

> Dirección promedio anual del viento en grados meteorológicos (0°–360°, donde 0°/360° = Norte).

- **Operación:** `180 + (180/π) * arctan2(u, v)`, resampleado a media anual
- **Unidades:** °
- **Máscara aplicada:** sí
- **Salida:** `Dir_Era5land.nc`

```python
dir_deg = 180 + (180/np.pi) * np.arctan2(u, v)
```

---

### 5. Dir90p — Dirección dominante de los vientos intensos

> Dirección promedio del viento filtrando únicamente los días donde la rapidez supera el percentil 90 del período completo.

- **Umbral:** RAP > p90 (percentil calculado sobre todo el período 2000–2024)
- **Operación:** Se filtran `u` y `v` con la máscara de vientos intensos, luego se aplica `arctan2`
- **Unidades:** °
- **Máscara aplicada:** sí
- **Salida:** `Dir_Era5land.nc`

> **Nota:** Este índice comparte nombre de archivo de salida con Dir (índice 4). Verificar si se requiere diferenciar los nombres de salida para evitar sobreescritura.

---

### 6. DVIn90p — Días con viento intenso

> Número de días al año donde la rapidez supera el percentil 90 del período completo (2000–2024).

- **Umbral:** RAP > p90 (percentil fijo sobre todo el período)
- **Operación:** conteo booleano anual con resampleo
- **Unidades:** días
- **Máscara aplicada:** sí
- **Salida:** `DVIn90p_Era5land.nc`

---

### 7. DVIb10p — Días con viento débil/calma

> Número de días al año donde la rapidez es inferior al percentil 10 del período completo (2000–2024).

- **Umbral:** RAP < p10 (percentil fijo sobre todo el período)
- **Operación:** conteo booleano anual con resampleo
- **Unidades:** días
- **Máscara aplicada:** sí
- **Salida:** `DVIb10p_Era5land.nc`

---

## Resumen de índices

| ID      | Nombre                     | Variable | Umbral / Operación         | Unidades | Percentil de referencia |
|---------|----------------------------|----------|----------------------------|----------|-------------------------|
| RAP_med | Rapidez media              | RAP      | media anual                | m/s      | —                       |
| RAP_mod | Moda de rapidez            | RAP      | moda anual                 | m/s      | —                       |
| RAP90p  | Vientos intensos           | RAP      | media donde RAP > p90      | m/s      | Anual (año a año)       |
| Dir     | Dirección dominante        | u, v     | arctan2, media anual       | °        | —                       |
| Dir90p  | Dirección vientos intensos | u, v     | arctan2 filtrado RAP > p90 | °        | Período completo        |
| DVIn90p | Días viento intenso        | RAP      | RAP > p90, conteo anual    | días     | Período completo        |
| DVIb10p | Días viento débil/calma    | RAP      | RAP < p10, conteo anual    | días     | Período completo        |

---

## Notas técnicas

- La rapidez `RAP` se deriva en tiempo de ejecución a partir de `u` y `v`; no se guarda como archivo intermedio.
- La conversión a dirección meteorológica usa `arctan2(u, v)` desplazado 180°, de modo que 0°/360° corresponde al Norte y los ángulos crecen en sentido horario.
- Para los índices DVIn90p y DVIb10p el percentil se calcula sobre el **período completo 2000–2024** (umbral histórico fijo), mientras que RAP90p usa el percentil calculado **dentro de cada año**.
- Los índices 6 y 7 usan `resample(time='Y')` en lugar de `'YE'` — verificar consistencia con los scripts de precipitación y temperatura que usan `'YE'` para evitar diferencias en la agrupación temporal al año bisiesto.
- El índice 4 (Dir) y el índice 5 (Dir90p) escriben en el mismo archivo `Dir_Era5land.nc`; se recomienda renombrar la salida de Dir90p a `Dir90p_Era5land.nc`.

---

## Ejecución

```bash
python Calculo_indices_climaticos_viento.py
```

Verificar que el directorio de salida exista antes de ejecutar:

```bash
mkdir -p "C:/Users/Ernesto/Downloads/prueba/extremos/Yucatan/Viento/"
```

---

## Referencias

- Sillmann, J. et al. (2013). Climate extremes indices in the CMIP5 multimodel ensemble. *Journal of Geophysical Research: Atmospheres*, 118.
- [Documentación xarray](https://docs.xarray.dev)
- [Documentación scipy.stats.mode](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mode.html)
- [ERA5-Land — Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
