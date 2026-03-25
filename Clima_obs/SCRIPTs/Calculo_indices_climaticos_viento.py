# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 15:12:04 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""





# =============================================================================
# Calculo de extremos 
# viento
# =============================================================================
# importamos las paqueterias necesarias
import xarray as xr
from scipy.stats import mode
import numpy as np
# =============================================================================
# Defino una funcion de mascara que usaré más tarde
# =============================================================================
def mask(ds):
    mascara_unos = (u[0]*0 + 1)
    ds = ds * mascara_unos
    return ds

def open_ds(dataset):
    variable = xr.open_dataset(dataset)
    var = list(variable.keys())[-1]
    variable = variable[var]
    try:
        variable = variable.rename({'valid_time': 'time'})
    except:
        print('no es necesario cambiar la dimension del tiempo')

    return variable

region = 'Yucatan'
u = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_u10m.nc')
v = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_v10m.nc')


output_wind = f'C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Viento/'

"""
Cálculo del los indices climaticos siguiendo 
Tabla 3. Índices de intensidad y de frecuencia de viento diario 
a utilizar, cada índice será calculado estacionalmente para cada año 
durante el periodo 2000-2024.

"""
# =============================================================================
# índices de intensidad de viento
#
# 1.  Rapidez media
#
# =============================================================================
RAP = np.sqrt(u**2 + v**2)

RAP_med = RAP.resample(time='YE').mean()

# RAP_med = mask(RAP_med)
RAP_med.attrs['definition'] = 'Rapidez media'
RAP_med.attrs['units'] = 'm/s'
RAP_med.name = 'Rap'
RAP_med.to_netcdf(f'{output_wind}/RAP_med_Era5land.nc')

# =============================================================================
# 2. Moda de la rapidez
# =============================================================================

def calcular_moda(x, axis):
    # mode() devuelve dos arrays: mode y count
    moda = mode(x, axis=axis, nan_policy='omit')
    return moda.mode

RAP_mod = RAP.resample(time='YE').reduce(calcular_moda, dim='time')
RAP_mod = mask(RAP_mod)
RAP_mod.attrs['definition'] = 'Rapidez moda'
RAP_mod.attrs['units'] = 'm/s'
RAP_med.name = 'Rapmoda'
RAP_med.to_netcdf(f'{output_wind}/RAP_mod_Era5land.nc')

# =============================================================================
# 3.  Vientos intensos
# =============================================================================
def calculate_R90p(year_data):
    RAP90 = year_data.quantile(0.90, dim='time', skipna=True)
    year_data = year_data.where(year_data > RAP90)
    return year_data.mean(dim='time', skipna=True)

# Agrupar por año y aplicar la función
RAP90p = RAP.groupby('time.year').map(calculate_R90p)
# Renombrar la dimensión para claridad
RAP90p = RAP90p.rename({'year': 'time'})
RAP90p = mask(RAP90p)
RAP90p.attrs['definition'] = 'Vientos intensos'
RAP90p.attrs['units'] = 'm/s'
RAP90p.name = 'Rap90p'
RAP90p.to_netcdf(f'{output_wind}/RAP90_mod_Era5land.nc')

# =============================================================================
# 4.Dirección dominante
# =============================================================================


dir_deg = 180 + (180/np.pi) * np.arctan2(u, v)
dir_deg = mask(dir_deg)
dir_deg.attrs['definition'] = 'Dirección dominante'
dir_deg.attrs['units'] = '°'
dir_deg.name = 'Dir'
dir_deg = dir_deg.resample(time='Y').mean()
dir_deg.to_netcdf(f'{output_wind}/Dir_Era5land.nc')

# =============================================================================
# 5.	Dirección dominante de los vientos intensos
# =============================================================================
RAP90 = RAP.quantile(0.90, dim='time', skipna=True)
filtro = RAP > RAP90
u_filtro = u.where(filtro)
v_filtro = v.where(filtro)
dir_deg90p = 180 + (180/np.pi) * np.arctan2(u_filtro, v_filtro)
dir_deg90p = dir_deg90p % 360
dir_deg90p = mask(dir_deg90p)
dir_deg90p.attrs['definition'] = 'Dirección dominante de los vientos intensos'
dir_deg90p.attrs['units'] = '°'
dir_deg90p.name = 'Dir90p'
dir_deg90p.to_netcdf(f'{output_wind}/Dir_Era5land.nc')
# =============================================================================
# 6.  Días con viento intenso
# =============================================================================
def DVIn(dataarray, q=0.90):
    p90 = dataarray.quantile(q, dim='time', skipna=True)
    exceedances = dataarray > p90
    counts_per_year = exceedances.resample(time='Y').sum()
    return counts_per_year


# Agrupar por año y aplicar la función
DVIn90p = DVIn(RAP)
DVIn90p = mask(DVIn90p)
DVIn90p.attrs['definition'] = 'Días con viento intenso'
DVIn90p.attrs['units'] = 'Days'
DVIn90p.name = 'Dir90p'
DVIn90p.to_netcdf(f'{output_wind}/DVIn90p_Era5land.nc')
# =============================================================================
# 7.  Días con viento débil/calma
# =============================================================================
def DVDb(dataarray, q=0.10):
    p10 = dataarray.quantile(q, dim='time', skipna=True)
    exceedances = dataarray < p10
    counts_per_year = exceedances.resample(time='Y').sum()
    return counts_per_year

DVIb10p = DVDb(RAP)
DVIb10p = mask(DVIb10p)
DVIb10p.attrs['definition'] = 'Días con viento débil/calma'
DVIb10p.attrs['units'] = 'Days'
DVIb10p.name = 'Dir90p'
DVIb10p.to_netcdf(f'{output_wind}/DVIb10p_Era5land.nc')

