# Catalogo_de_Formulas_y_Scripts.docx

**Autores:** Ernesto Ramos Esteban y Gabriela Colorado Ruíz.
**Fecha:** Febrero 2026

---

## 1. Descarga de los datos
Se descargaron datos desde el portal de Copernicus, disponible en:
https://cds.climate.copernicus.eu/datasets/derived-era5-land-daily-statistics?tab=download

Es posible descargar los datos directamente desde el portal, pero para automatizar 
la descarga se generó un script en Python que selecciona la variable, la región y el 
periodo de tiempo analizado, guardando los resultados en archivos NetCDF.

Los términos de uso deben ser aceptados la primera vez que se descargan los datos.
Para poder descargar es necesario contar con una clave personal (URL y clave personal).
-URL: https://cds.climate.copernicus.eu/api
-API KEY: ***********************

Se generó el script `Download_tmax_tmin_tmean_wind.py` para la descarga automática 
de los datos del ERA5 Land para las variables de temperatura máxima, temperatura mínima, 
temperatura media y componentes u y v del viento a 10 metros.

En el script se selecciona una de las dos regiones: **Nayarit** o **Yucatán**. 
Además, se define la zona horaria `utc-07:00`.

> ⚠️ La precipitación se descargó de forma distinta, ya que el portal de Copernicus 
> no permite acumularla a escala diaria de forma directa. *(En proceso)*


## 2. Procesamiento de los datos
Con ayuda del script 'procesamiento_nombre_recortes_conversion.py' se realizaron las siguientes operaciones:

- **Recorte** de los datos a la región del Estado correspondiente.
- **Conversión de unidades** de Kelvin a Celsius para las variables de temperatura.
- **Renombrado de variables**: por defecto Copernicus entrega las variables de 
  temperatura como `t2m`; se renombran a `tmax`, `tmin` y `tmean` según corresponda.

Estos pasos permiten preparar los datos para el posterior cálculo de las series 
de tiempo por Estado.




## 3. Calculo de extremos de temperatura
Basados en los índices de intensidad y de frecuencia de temperatura mínima y máxima 
diaria, se calcularon los índices climáticos de temperatura a escala anual con Python.

Cada índice fue calculado estacionalmente para cada año durante el periodo **2000–2024**

