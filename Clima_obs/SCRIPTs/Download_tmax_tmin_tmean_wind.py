# -*- coding: utf-8 -*-
"""
Created on Fri Feb  6 08:17:19 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""

# =============================================================================
# Programa para descargar datos de ERA5Land
# para Yucatán y Nayarit
# =============================================================================

# =============================================================================
# URL y Clave personal
URL = 'https://cds.climate.copernicus.eu/api'
KEY = '4d6a1aeb-8c4f-44cd-aad6-7f635fd847e0'
# =============================================================================
import cdsapi
import numpy as np

dataset = "derived-era5-land-daily-statistics"
# Años necesarios
years = np.arange(2025,2026)
# dicionario con las variables en nombre corto y el nombre de la estadistica en
# la interfaz de copernicus

VARIABLES = {
    "tmax": "daily_max",
    "tmin": "daily_min",
    "tmean": "daily_mean",
    "u10m": "daily_mean",  
    "v10m": "daily_mean",  

}
# opcion 1
# region = 'Nayarit'
# opcion 2
region = 'Yucatan'

for var, var_name in VARIABLES.items():
    for year in years:
        #seleccion de la variable
        if var == "u10m":
            cds_variable = "10m_u_component_of_wind"
        elif var == "v10m":
            cds_variable = "10m_v_component_of_wind"
        else:
            cds_variable = "2m_temperature"
        # seleccionamos la region
        if region =='Nayarit':
            region_variable  = [23.2, -106, 20.5, -103.6]
        elif region =='Yucatan':
            region_variable  = [21.7, -90.5, 19.3, -87.2]
        else :
            print(f'region incorrecta: {region}')
            break
        request = {
            # variable a procesar
            "variable": [cds_variable],            
            # Anio
            "year": f'{year}',
            # Meses necesarios
            "month": ["01", "02", "03",
                    "04", "05", "06",
                    "07", "08", "09",
                    "10", "11", "12"],
            # Todos los dias del mes
            "day": [
                "01", "02", "03",
                "04", "05", "06",
                "07", "08", "09",
                "10", "11", "12",
                "13", "14", "15",
                "16", "17", "18",
                "19", "20", "21",
                "22", "23", "24",
                "25", "26", "27",
                "28", "29", "30",
                "31"
            ],
            # estadistica (min,max,media) : variable
            "daily_statistic": f"{var_name}",
            # zona horaria
            "time_zone": "utc-07:00",
            # frecuencia de los datos para le promedio diario
            # 3 horas,6 horas, 1 hora
            "frequency": "6_hourly",
            # region de estudio
            "area": region_variable

        }
        # Api para conectarse a Copernicus
        client = cdsapi.Client(url=URL, key=KEY)
        client.retrieve(dataset, request).download(f'C:/Users/Ernesto/Documents/prueba/{region}_{year}_{var}.nc')
