# -*- coding: utf-8 -*-
"""
Created on Tue Mar  3 08:52:19 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""


# =============================================================================
# Calculo de extremos anuales
# =============================================================================
# importamos las paqueterias necesarias
import xarray as xr
import os
import icclim
from xclim.core.calendar import percentile_doy
from xclim.indices import tg90p
from xclim.indices import tg10p
import xarray as xr 
import geopandas as gpd
from shapely.geometry import mapping
import numpy as np
# =============================================================================
# Defino una funcion de mascara que usaré más tarde
# =============================================================================
def mask(ds):
    mascara_unos = (pr[0]*0 + 1)
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


# region = 'Nayarit'
region = 'Yucatan'
pr = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_pr.nc')


output_pr = f'C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Precipitacion/'

"""
Cálculo del los indices climaticos siguiendo 
Tabla 1. Índices de intensidad y de frecuencia de precipitación 
a utilizar, cada índice será calculado estacionalmente 
para cada año durante el periodo 2000-2024
"""

# =============================================================================
# índices de intensidad
#
#   1.  Lluvia acumulada
#
# =============================================================================

prcptot = icclim.prcptot(pr)
prcptot = mask(prcptot['PRCPTOT'])
prcptot.attrs['definition'] = 'Lluvia acumulada'
prcptot.attrs['units'] = 'mm'
prcptot.name = 'PRCPTOT'
prcptot.to_netcdf(f'{output_pr}PRCPTOT_Era5land.nc')
# =============================================================================
# 
# 3.	Lluvia máxima de un día (*)
# =============================================================================

rx1d = icclim.rx1day(pr)
rx1d = mask(rx1d['RX1day'])
rx1d.attrs['definition'] = 'Lluvia máxima de un día'
rx1d.attrs['units'] = 'mm'
rx1d.name = 'RX1day'
rx1d.to_netcdf(f'{output_pr}rx1day_Era5land.nc')
# =============================================================================
# 
#   4.	Precipitación de días muy húmedos (*)
#
# =============================================================================
wet_days_ref = pr.where(pr >= 1.0)
#  Calcular el percentil 95 de precipitación en días húmedos para todo el período de referencia
RRwn95 = wet_days_ref.quantile(0.95, dim='time', skipna=True)

def calculate_r95p(year_data):
    # Identificar días húmedos (RR ≥ 1.0mm)
    wet_days = year_data.where(year_data >= 1.0)
    # Seleccionar solo días donde precipitación > RRwn95
    extreme_wet_days = wet_days.where(wet_days > RRwn95)
    # Sumar las precipitaciones extremas
    return extreme_wet_days.sum(dim='time', skipna=True)

# Agrupar por año y aplicar la función
r95p = pr.groupby('time.year').map(calculate_r95p)
# Renombrar la dimensión para claridad
r95p = r95p.rename({'year': 'time'})
r95p = mask(r95p)
r95p.attrs['definition'] = 'Lluvia máxima de un día'
r95p.attrs['units'] = 'mm'
r95p.name = 'R95p'
r95p.to_netcdf(f'{output_pr}r95p_Era5land.nc')
# =============================================================================
# 6.  Días consecutivos secos (*)
# =============================================================================

cdd = icclim.cdd(pr)
cdd = mask(cdd['CDD'])
cdd.attrs['definition'] = 'Días consecutivos secos'
cdd.attrs['units'] = 'Days'
cdd.name = 'CDD'
cdd.to_netcdf(f'{output_pr}cdd_Era5land.nc')
# =============================================================================
# 7.  Días consecutivos húmedos (*)
# =============================================================================
cwd = icclim.cwd(pr)
cwd = mask(cwd['CWD'])
cwd.attrs['definition'] = 'Días consecutivos húmedos'
cwd.attrs['units'] = 'Days'
cwd.name = 'CWD'
cwd.to_netcdf(f'{output_pr}cwd_Era5land.nc')
# =============================================================================
# 8.  Días con lluvia intensa
# =============================================================================
r10mm = icclim.r10mm(pr)
r10mm = mask(r10mm['R10mm'])
r10mm.attrs['definition'] = 'Días con lluvia intensa'
r10mm.attrs['units'] = 'Days'
r10mm.name = 'R10mm'
r10mm.to_netcdf(f'{output_pr}r10mm_Era5land.nc')
# =============================================================================
# 9.  Días con lluvia muy intensa
# =============================================================================
r20mm = icclim.r20mm(pr)
r20mm = mask(r20mm['R20mm'])
r20mm.attrs['definition'] = 'Días con lluvia muy intensa'
r20mm.attrs['units'] = 'Days'
r20mm.name = 'R20mm'
r20mm.to_netcdf(f'{output_pr}r20mm_Era5land.nc')