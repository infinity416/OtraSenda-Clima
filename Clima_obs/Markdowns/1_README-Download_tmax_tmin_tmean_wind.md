# Script Download_tmax_tmin_tmean_wind.py

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx | raesern@gmail.com  
**Departamento:** Oceanografía Física, CICESE  
**Fecha de creación:** 6 de febrero de 2026

---

## Descripción general

Este script descarga datos diarios de **temperatura y viento** del conjunto de datos
`derived-era5-land-daily-statistics` desde el portal de Copernicus, para el periodo
definido por el usuario.

Los datos se descargan en formato **NetCDF**, organizados en archivos por variable y año.

---

## Requisitos

- Python 3.x
- Librerías: `cdsapi`, `numpy`
- Cuenta activa en el portal de Copernicus con URL y clave personal configuradas

---

## Variables descargadas

| Nombre corto | Variable en Copernicus         | Estadística diaria |
|--------------|--------------------------------|--------------------|
| `tmax`       | `2m_temperature`               | Máxima diaria      |
| `tmin`       | `2m_temperature`               | Mínima diaria      |
| `tmean`      | `2m_temperature`               | Media diaria       |
| `u10m`       | `10m_u_component_of_wind`      | Media diaria       |
| `v10m`       | `10m_v_component_of_wind`      | Media diaria       |

---

## Uso

### 1. Configurar credenciales

Al inicio del script se deben definir la URL y la clave personal de Copernicus
en las variables `URL` y `KEY`.

### 2. Seleccionar la región

Activar una de las dos regiones disponibles editando la variable `region`:

- `'Nayarit'` — coordenadas: Norte 23.2°, Oeste 106°, Sur 20.5°, Este 103.6°
- `'Yucatan'` — coordenadas: Norte 21.7°, Oeste 90.5°, Sur 19.3°, Este 87.2°

### 3. Ejecutar el script

El script itera automáticamente sobre todas las variables y años definidos.
Por cada combinación genera un archivo con el formato:
```
{region}_{año}_{variable}.nc
```

Por ejemplo: `Nayarit_2025_tmax.nc` corresponde a la temperatura máxima 
diaria de 2025 en Nayarit.

### 4. Ruta de salida

Los archivos se guardan en la ruta definida dentro del script. Modificarla 
antes de ejecutar si es necesario.

---

## Notas

> ⚠️ La frecuencia base utilizada para calcular las estadísticas diarias es 
> de **6 horas**, con zona horaria `utc-07:00`.