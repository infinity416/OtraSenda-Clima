# -*- coding: utf-8 -*-
"""
Created on Mon Feb  9 14:28:12 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""

# =============================================================================
# importo las paqueterias necesarias
# =============================================================================
import xarray as xr 
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
variables = ["tmax", "tmin", "tmean", "u10m", "v10m"]
region = 'Nayarit'
# region = 'Yucatan'
for var in variables:
    path = f'C:/Users/Ernesto/Downloads/prueba/{region}_2???_{var}.nc'
    
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
    print(f"recortando {region}")
    # convertir unidades de temperatura de Kelvin a ° C
    if variable_corr =='tmax' or variable_corr =='tmin' or variable_corr=='tmean':
        data[variable_corr] = data[variable_corr] - 273.15
    data_region = mask(data[variable_corr],f'{region}')
    print("datos guardados en:")
    data_region.to_netcdf(f'C:/Users/Ernesto/Documents/prueba/{region}/{region}_2000-2024_{var}.nc')
