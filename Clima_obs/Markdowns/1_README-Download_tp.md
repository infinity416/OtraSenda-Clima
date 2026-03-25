# Download_tp.py

**Autor:** Ernesto Ramos Esteban  
**Contacto:** ramos-ernesto@cicese.edu.mx | raesern@gmail.com  
**Departamento:** Oceanografía Física, CICESE  
**Fecha de creación:** 10 de febrero de 2026

---

## Descripción general

Este script descarga datos horarios de **precipitación total** del conjunto de datos 
`reanalysis-era5-land` desde el portal de Copernicus, para el periodo **1999–2025**.

Los datos se descargan en formato **NetCDF**, organizados en archivos semestrales 
por región.

---

## Requisitos

- Python 3.x
- Librerías: `cdsapi`, `numpy`
- Cuenta activa en el portal de Copernicus con clave personal configurada

---

## Uso

### 1. Seleccionar la región

Antes de ejecutar el script, se debe activar una de las dos regiones disponibles 
editando la variable `region`:

- `'Nayarit'` — coordenadas: Norte 23.2°, Oeste 106°, Sur 20.5°, Este 103.6°
- `'Yucatan'` — coordenadas: Norte 21.7°, Oeste 90.5°, Sur 19.3°, Este 87.2°

### 2. Ejecutar el script

El script itera automáticamente sobre todos los años y semestres del periodo definido. 
Por cada combinación genera un archivo con el formato:
```
{region}_{año}_{semestre}.nc
```

Por ejemplo: `Yucatan_2005_1.nc` corresponde al primer semestre de 2005 en Yucatán.

### 3. Ruta de salida

Los archivos se guardan en la ruta definida dentro del script. Modificarla antes 
de ejecutar si es necesario.

---

## Notas

> ⚠️ La API de Copernicus no permite acumular la precipitación a escala diaria de 
> forma directa, por eso se descargan los datos a resolución **horaria** para 
> realizar la acumulación en un paso posterior.