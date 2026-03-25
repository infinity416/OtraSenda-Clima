# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 08:25:30 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""


# =============================================================================
# importo las paqueterias necesarias
# =============================================================================
import xarray as xr 
import pandas as pd
import geopandas as gpd
from shapely.geometry import mapping
# =============================================================================
# Defino una funcion de mascara que usaré más tarde
# =============================================================================
def mask(change,region):
    try:
        change = change.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)    
    except:
        change = change.rio.set_spatial_dims(x_dim="longitude", y_dim="latitude", inplace=True)
        
    change = change.rio.write_crs("EPSG:4326", inplace=True)
    mask=gpd.read_file('C:/users/ernesto/Downloads/DI_export_mex/MX_Estados_WGS84_DI8_region.shp')
    if region =='Yucatan': 
        mask = mask[mask.NOMBRE == 'Yucatán']
    elif region =='Nayarit':
        mask = mask[mask.NOMBRE == 'Nayarit']

    change_mask = change.rio.clip(mask.geometry.apply(mapping), mask.crs)
    return change_mask

# =============================================================================
# procesamiento para renombrar las variables de forma correctao
# por defecto todas las temperaturas son t2m
# =============================================================================
variables = ["pr"]
#region = 'Nayarit'
region = 'Yucatan'
for var in variables:
#    path = f'C:/Users/Ernesto/Downloads/prueba/{region}_2???_{var}.nc'
    path = f'C:/Users/Ernesto/Downloads/prueba/{region}_????_?.nc'
    
    data = xr.open_mfdataset(path)
    
    variable = list(data)[-1]
    print(f" Nombre original de la variable: '{variable}' Se corregirá a: '{var}'")

    data = data.rename({variable:f'{var}'})
    variable_corr = list(data)[-1]
    print(f" Variable corregida: '{variable_corr}' (antes: '{variable}')")
    # renombramos la dimension del tiempo de valid_time a time
    data  = data.rename({'valid_time':
                          'time'})
    # Recortando area para el estado
    
    #corregimos el tiempo
    time_utc = pd.to_datetime(data['time'].values).tz_localize('UTC')

    # Convierte a la zona horaria UTC-7 (zona horaria fija, cuidado con horario de verano)
    time_utc7 = time_utc.tz_convert('Etc/GMT+7')
        
    time_utc7_naive = time_utc7.tz_localize(None)
    
    data_corr = data.assign_coords(valid_time=time_utc7_naive)
    data_corr = data_corr.sel(time=slice('2000',
                              '2024'))    
    data_corr = data_corr.diff(dim='valid_time')
    data_corr = data_corr.resample(time='1H').ffill().diff('valid_time')
    data_corr = data_corr.where(data_corr >= 0, 0)
    data_corr = data_corr.resample(time='1D').sum()
    data_corr[var] = data_corr[var]*1000
    data_corr[var]['units'] = 'mm'
    print(f"recortando {region}")               
    data_region = mask(data_corr[variable_corr],f'{region}')
    print("datos guardados en:")
    data_region.to_netcdf(f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_{var}.nc')
