# Cálculo de Índices Climáticos de Temperatura

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx · raesern@gmail.com  
**Institución:** Departamento de Oceanografía Física, CICESE  
**Última actualización:** Febrero 2026

---

## Descripción general

Script en Python para el cálculo de índices climáticos de extremos de temperatura a partir de datos de reanálisis ERA5-Land. Los índices siguen el estándar internacional ETCCDI (Expert Team on Climate Change Detection and Indices) y se calculan de forma anual para el período 2000–2024 usando temperatura máxima, mínima y media diaria.

---

## Dependencias

| Paquete  | Uso principal                                     |
|----------|---------------------------------------------------|
| `xarray` | Lectura, manipulación y resampleo de datos NetCDF |
| `icclim` | Cálculo del índice WSDI                           |

Instalación recomendada con conda:

```bash
conda install -c conda-forge xarray icclim
```

---

## Estructura de archivos

### Entrada

```
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmax.nc
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmin.nc
C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmean.nc
```

Tres archivos NetCDF de ERA5-Land con resolución diaria: temperatura máxima (`Tmax`), temperatura mínima (`Tmin`) y temperatura media (`Tmed`). La dimensión temporal puede llamarse `time` o `valid_time`.

### Salida

```
C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Temperatura/
├── Tmx_Era5land.nc
├── Tmn_Era5land.nc
├── TXx_Era5land.nc
├── TNn_Era5land.nc
├── DTR_Era5land.nc
├── SU_Era5land.nc
├── TR_Era5land.nc
└── WSDI_Era5land.nc
```

Cada archivo NetCDF de salida incluye atributos `definición` y `units`.

---

## Configuración

```python
region = 'Yucatan'   # Opciones: 'Nayarit', 'Yucatan', u otra región disponible
```

Los directorios de entrada y salida se construyen dinámicamente. **El directorio de salida debe existir previamente.**

---

## Funciones auxiliares

### `open_ds(dataset)`

Abre un archivo NetCDF y extrae la variable climática principal.

- **Entrada:** ruta al archivo `.nc`
- **Salida:** `xarray.DataArray` con la variable de temperatura
- **Nota:** Renombra automáticamente `valid_time` → `time` cuando es necesario (ERA5 descargado desde el CDS de Copernicus)

### `mask(ds)`

Aplica una máscara geográfica usando el primer paso de tiempo de `Tmax`. Asigna `NaN` fuera del dominio regional de interés, evitando que píxeles exteriores aparezcan con valor `0` en los índices de frecuencia.

- **Entrada:** `xarray.DataArray`
- **Salida:** `xarray.DataArray` enmascarado
- **Nota:** Esta corrección fue especialmente necesaria para los índices SU y TR, donde la ausencia de datos fuera del estado se interpretaba como cero días, distorsionando los resultados espaciales.

---

## Índices calculados

### 1. Tmx — Temperatura máxima promedio anual

> Valor máximo de la temperatura media diaria en el año.

- **Variable de entrada:** `Tmed`
- **Operación:** `resample(time='YE').max()`
- **Unidades:** °C
- **Salida:** `Tmx_Era5land.nc`

---

### 2. Tmn — Temperatura mínima promedio anual

> Valor mínimo de la temperatura media diaria en el año.

- **Variable de entrada:** `Tmed`
- **Operación:** `resample(time='YE').min()`
- **Unidades:** °C
- **Salida:** `Tmn_Era5land.nc`

---

### 3. TXx — Máximo de la temperatura máxima

> Valor más alto registrado por la temperatura máxima diaria en el año.

- **Variable de entrada:** `Tmax`
- **Operación:** `resample(time='YE').max()`
- **Unidades:** °C
- **Salida:** `TXx_Era5land.nc`

---

### 4. TNn — Mínimo de la temperatura mínima

> Valor más bajo registrado por la temperatura mínima diaria en el año.

- **Variable de entrada:** `Tmin`
- **Operación:** `resample(time='YE').min()`
- **Unidades:** °C
- **Salida:** `TNn_Era5land.nc`

---

### 5. DTR — Rango diurno de temperatura

> Diferencia promedio anual entre temperatura máxima y mínima diaria.

- **Variables de entrada:** `Tmax`, `Tmin`
- **Operación:** `(Tmax - Tmin).resample(time='YE').mean()`
- **Unidades:** °C
- **Salida:** `DTR_Era5land.nc`

---

### 6. SU — Días de verano

> Número de días al año con temperatura máxima superior a 30 °C.

- **Variable de entrada:** `Tmax`
- **Umbral:** TX > 30 °C
- **Operación:** conteo booleano anual con resampleo
- **Unidades:** días
- **Máscara aplicada:** sí
- **Salida:** `SU_Era5land.nc`

```python
hot_days = Tmax > 30
SU = hot_days.resample(time='YE').sum(dim="time")
```

---

### 7. TR — Noches tropicales

> Número de noches al año con temperatura mínima superior a 20 °C.

- **Variable de entrada:** `Tmin`
- **Umbral:** TN > 20 °C
- **Operación:** conteo booleano anual con resampleo
- **Unidades:** días
- **Máscara aplicada:** sí
- **Salida:** `TR_Era5land.nc`

```python
tropical_nights = Tmin > 20
TR = tropical_nights.resample(time='YE').sum(dim="time")
```

---

### 8. TX90p — Días cálidos *(externo)*

> Porcentaje de días con temperatura máxima superior al percentil 90.  
> Calculado con **Climate Data Operators (CDO)**, no en este script.

---

### 9. TN10p — Noches frías *(externo)*

> Porcentaje de días con temperatura mínima inferior al percentil 10.  
> Calculado con **Climate Data Operators (CDO)**, no en este script.

---

### 10. WSDI — Duración de olas de calor

> Número anual de días que forman parte de períodos de al menos 6 días consecutivos donde TX > percentil 90 de la temperatura máxima.

- **Variable de entrada:** `Tmax`
- **Función:** `icclim.wsdi(Tmax)`
- **Máscara aplicada:** sí
- **Salida:** `WSDI_Era5land.nc`

---

## Resumen de índices

| ID    | Nombre                 | Variable    | Umbral / Operación | Unidades | Fuente |
|-------|------------------------|-------------|--------------------|----------|--------|
| Tmx   | Temp. máxima promedio  | Tmed        | max anual          | °C       | xarray |
| Tmn   | Temp. mínima promedio  | Tmed        | min anual          | °C       | xarray |
| TXx   | Máximo de Tmax         | Tmax        | max anual          | °C       | xarray |
| TNn   | Mínimo de Tmin         | Tmin        | min anual          | °C       | xarray |
| DTR   | Rango diurno           | Tmax − Tmin | media anual        | °C       | xarray |
| SU    | Días de verano         | Tmax        | TX > 30 °C         | días     | xarray |
| TR    | Noches tropicales      | Tmin        | TN > 20 °C         | días     | xarray |
| TX90p | Días cálidos           | Tmax        | TX > p90           | %        | CDO    |
| TN10p | Noches frías           | Tmin        | TN < p10           | %        | CDO    |
| WSDI  | Duración olas de calor | Tmax        | ≥6 días TX > p90   | días     | icclim |

---

## Notas técnicas

- El resampleo temporal usa la frecuencia `'YE'` (year-end), que agrupa por año calendario completo.
- Los índices SU y TR se calculan mediante operaciones booleanas; la función `mask()` es **indispensable** para estos índices, ya que sin ella los píxeles fuera del dominio toman valor `0` en lugar de `NaN`, generando falsos resultados espaciales.
- Los índices TX90p y TN10p (8 y 9) se calcularon externamente con CDO y quedan referenciados en el script como comentario para mantener la trazabilidad metodológica completa.
- El percentil base para WSDI lo calcula internamente `icclim` sobre el período completo del dataset.

---

## Ejecución

```bash
python Calculo_indices_climaticos_temperatura.py
```

Verificar que el directorio de salida exista antes de ejecutar:

```bash
mkdir -p "C:/Users/Ernesto/Downloads/prueba/extremos/Yucatan/Temperatura/"
```

---

## Referencias

- Sillmann, J. et al. (2013). Climate extremes indices in the CMIP5 multimodel ensemble. *Journal of Geophysical Research: Atmospheres*, 118.
- [Documentación icclim](https://icclim.readthedocs.io)
- [Climate Data Operators (CDO)](https://code.mpimet.mpg.de/projects/cdo)
- [ERA5-Land — Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
