# -*- coding: utf-8 -*-
"""
Created on Tue Feb 10 14:12:51 2026

@author: Ernesto Ramos Esteban
ramos-ernesto@cicese.edu.mx
raesern@gmail.com
Departamento de Oceanografía Física, CICESE
"""


import cdsapi
import numpy as np
years = np.arange(1999, 2026)

semesters = {
    "1": ["01", "02", "03", "04", "05", "06"],  
    "2": ["07", "08", "09", "10", "11", "12"]   
}
dataset = "reanalysis-era5-land"

region = 'Yucatan'
# region = 'Nayarit'
for year in years:
    for semester, months in semesters.items():
        if region =='Nayarit':
            region_variable  = [23.2, -106, 20.5, -103.6]
        elif region =='Yucatan':
            region_variable  = [21.7, -90.5, 19.3, -87.2]
        else :
            print(f'region incorrecta: {region}')
        request = {
            "variable": ["total_precipitation"],
            "year": f"{year}",
            "month": months,
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
            "time": [
                "00:00", "01:00", "02:00",
                "03:00", "04:00", "05:00",
                "06:00", "07:00", "08:00",
                "09:00", "10:00", "11:00",
                "12:00", "13:00", "14:00",
                "15:00", "16:00", "17:00",
                "18:00", "19:00", "20:00",
                "21:00", "22:00", "23:00"
            ],
            "data_format": "netcdf",
            "download_format": "unarchived",
            "area": region_variable
        }
        
        client = cdsapi.Client()
        client.retrieve(dataset, request).download(f'C:/Users/Ernesto/Downloads/prueba/{region}_{year}_{semester}.nc')
    
