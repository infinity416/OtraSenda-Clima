# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 13:04:20 2026

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
import icclim
# =============================================================================
# Defino una funcion de mascara que usaré más tarde
# =============================================================================
def mask(ds):
    mascara_unos = (Tmax[0]*0 + 1)
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

Tmax = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmax.nc')
Tmin = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmin.nc')
Tmed = open_ds(
    f'C:/Users/Ernesto/Downloads/prueba/{region}/{region}_2000-2024_tmean.nc')

output_temp = f'C:/Users/Ernesto/Downloads/prueba/extremos/{region}/Temperatura/'

"""
Cálculo del los indices climaticos siguiendo 
Tabla 1. Índices de intensidad y de frecuencia de temperatura mínima 
y máxima diaria a utilizar, cada índice será calculado estacionalmente 
para cada año durante el periodo 2000-2024
"""
# =============================================================================
# índices de intensidad
#
# 1.  Temperatura máxima promedio
#
# =============================================================================
Tmx = (Tmed).resample(time='YE').max()
Tmx.name = 'Tmx'
Tmx.attrs['definición'] = 'Temperatura máxima promedio'
Tmx.attrs['units'] = '° C'
Tmx.to_netcdf(f'{output_temp}/Tmx_Era5land.nc')
# =============================================================================
# 2.  Temperatura mínima promedio
# =============================================================================
Tmn = (Tmed).resample(time='YE').min()
Tmn.attrs['definición'] = 'Temperatura mínima promedio'
Tmn.attrs['units'] = '° C'
Tmn.name = 'Tmn'
Tmn.to_netcdf(f'{output_temp}/Tmn_Era5land.nc')
# =============================================================================
# 3. Máximo de la temperatura máxima
# =============================================================================
TXx = Tmax.resample(time='YE').max()
TXx.attrs['definición'] = 'Máximo de la temperatura máxima'
TXx.attrs['units'] = '° C'
TXx.name = 'TXx'
TXx.to_netcdf(f'{output_temp}/TXx_Era5land.nc')
# =============================================================================
# 4.	Mínimo de la temperatura Mínima
# =============================================================================
TNn = Tmin.resample(time='YE').min()
TNn.attrs['definición'] = 'Mínimo de la temperatura Mínima'
TNn.attrs['units'] = '° C'
TNn.name = 'TNn'
TNn.to_netcdf(f'{output_temp}/TNn_Era5land.nc')
# =============================================================================
# 5.	Rango diurno de temperatura.
# =============================================================================
DTR = (Tmax - Tmin).resample(time='YE').mean()
DTR.attrs['definición'] = 'Rango diurno de temperatura'
DTR.attrs['units'] = '° C'
DTR.name = 'DTR'
DTR.to_netcdf(f'{output_temp}/DTR_Era5land.nc')
# =============================================================================
#  Índices de Frecuencia
#
# 6.  Número de días de verano 
#
# =============================================================================
hot_days = Tmax > 30
SU = hot_days.resample(time='YE').sum(dim="time")
SU.attrs['definición'] = 'Número de días de verano'
SU.attrs['units'] = 'Days'

# esta mascara fue necesaria, porque todo fuera del estado daba 0,
# quizá hay una mejor forma de corregir eso, pero en su momento lo
# solucione mutiplicando por 1 las regiones dentro del estado y 
# por nan lo que está fuera de la región de interés
SU = mask(SU)
SU.name = 'SU'
SU.to_netcdf(f'{output_temp}/SU_Era5land.nc')
# =============================================================================
# 7. Número de noches tropicales
# =============================================================================
tropical_nights = Tmin >20
TR = tropical_nights.resample(time='YE').sum(dim="time")
TR.attrs['definición'] = 'Número de noches tropicales'
TR.attrs['units'] = 'Days'
TR = mask(TR)
TR.name = 'TR'
TR.to_netcdf(f'{output_temp}/TR_Era5land.nc')
# =============================================================================
# 
# =============================================================================

# =============================================================================
# 
# =============================================================================
# Los indices 8 y 9 se calcularon con Climate Ddata Operators (CDO)
# 8.  Días cálidos (TX90p)
# 9.  Noches frías (TN10p)
# =============================================================================
# 10.  Duración de olas de calor
# =============================================================================
wsdi = icclim.wsdi(Tmax)
wsdi = mask(wsdi['WSDI'])
wsdi.name = 'WSDI'
wsdi.to_netcdf(f'{output_temp}/WSDI_Era5land.nc')




