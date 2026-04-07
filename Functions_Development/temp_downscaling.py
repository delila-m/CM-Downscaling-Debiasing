# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 14:14:21 2026

@author: delil
"""

# Load libraries
import numpy as np
import xarray as xr
import bisect as bi
import matplotlib.pyplot as plt

# Load the iTRACE
data_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/atm-surface/itrace.11Ka-0Ka.atm.TREFHT.nc")



# brute force test if xarray's interpolation function works the same...
test = data_xarray.TREFHT_ANN.interp(lon=[355], lat =[-23.684210526315795], method = "linear")
test

control = data_xarray.isel(lon = slice(141, 143), lat = slice(94, 95)).sel(time = "0031-02-15")
control.lat.values

range = [0,1]

for i in range:
    for j in range:
        print(f"lat: {control.lat.values[i]}")
        print(f"lon: {control.lon.values[j]}")
        print(f"value {control.TREFHT_ANN.isel(lat = [i], lon = [j]).values}\n")
        
x = 355
y = -23.684210526315795        
x1 = 352.5
x2 = 355.0
y1 = -23.684210526315795
y2 = -21.789473684210535
q11 = 292.56185913
q12 = 292.72225952
q21 = 292.22451782
q22 = 292.41482544

r2 = q12*(x2-x)/(x2-x1) + q22*(x-x1)/(x2-x1)
r1 = q11*(x2-x)/(x2-x1) + q21*(x-x1)/(x2-x1)

p = r1*(y2-y)/(y2-y1) + r2*(y-y1)/(y2-y1)
p #292.22451782

# bilinear interpolation function arguments:
    # coordinates for point to be interpolated
    # climate model data as an xarray object
        # would it be worthwhile to pass attribute names??
def bilinear_interpolation( x, y, cm_xarray ):
    
    # find nearest coords to desired interpolation point 
    q_coords = find_q_coords(x, y, cm_xarray)
            
    # grab data values for Q11, Q12, Q21, Q22 using given coordinates 
    
    
    # calculate R1 & R1
    
    # calculate and return P (interpolated point)


# internal function to find the coordinates of the q points,
    # or the four closest points to the interpolated point 
def find_q_coords( x, y, cm_xarray ):   
    
    # grab length of lat & long for future use 
    lat_len = len(cm_xarray.lat)
    lon_len = len(cm_xarray.lon)
    
    # check if point is inside range 
    if not cm_xarray.lon.values[0] <= x <= cm_xarray.lon.values[lon_len-1]:
        print(f"Invalid Longitude. {x} Outside of range")
        return np.nan
    if not cm_xarray.lat.values[0] <= y <= cm_xarray.lat.values[lat_len-1]:
        print(f"Invalid Longitude. {y} Outside of range")
        return np.nan
    
    # locate longitude insertion point bounds using bisect
    bi_lon_index = bi.bisect(cm_xarray.lon, x) 
    
    # check to see if the index value is outside longitude range
    if bi_lon_index == lon_len:  
        # if outside of range, subtract 1 from index value
        bi_lon_index -= 1   
    
    # locate latitde insertion point using same method 
    bi_lat_index = bi.bisect(cm_xarray.lat, y)
    
    if bi_lat_index == lat_len:
        bi_lat_index -= 1
    
    # return x1, x2, y1, y2
    return {'x1': cm_xarray.lon.values[bi_lon_index - 1],
            'x2': cm_xarray.lon.values[bi_lon_index],
            'y1': cm_xarray.lat.values[bi_lat_index - 1],
            'y2':  cm_xarray.lat.values[bi_lat_index]}

q_test = find_q_coords(1, 85, data_xarray)
q_test        
    
    
    
    
    




















