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

# bilinear interpolation function arguments:
    # coordinates for point to be interpolated
    # climate model data as an xarray object
        # would it be worthwhile to pass attribute names??
def bilinear_interpolation( x, y, cm_xarray ):
    
    # find nearest coords to desired interpolation point 
    q_coords = find_q_coords(x, y, cm_xarray)
            
    # grab data values for Q11, Q12, Q21, Q22 using given coordinates 
    q11 = cm_xarray.TREFHT_ANN.sel(lon = q_coords['x1'], lat = q_coords['y1'], method = 'nearest') 
    q12 = cm_xarray.TREFHT_ANN.sel(lon = q_coords['x1'], lat = q_coords['y2'], method = 'nearest') 
    q21 = cm_xarray.TREFHT_ANN.sel(lon = q_coords['x2'], lat = q_coords['y1'], method = 'nearest') 
    q22 = cm_xarray.TREFHT_ANN.sel(lon = q_coords['x2'], lat = q_coords['y2'], method = 'nearest') 
    
    # calculate R1 & R2
    r1 = q11*(q_coords['x2']-x)/(q_coords['x2']-q_coords['x1']) + q21*(x-q_coords['x1'])/(q_coords['x2']-q_coords['x1'])
    r2 = q12*(q_coords['x2']-x)/(q_coords['x2']-q_coords['x1']) + q22*(x-q_coords['x1'])/(q_coords['x2']-q_coords['x1'])

    
    # calculate and return P (interpolated point)
    p = r1*(q_coords['y2']-y)/(q_coords['y2']-q_coords['y1']) + r2*(y-q_coords['y1'])/(q_coords['y2']-q_coords['y1'])
    return p


# internal function to find the coordinates of the q points,
    # or the four closest points to the interpolated point 
def find_q_coords( x, y, cm_xarray ):   
    
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
    if bi_lon_index == len(cm_xarray.lon) 
        # if outside of range, subtract 1 from index value
        bi_lon_index -= 1   
    
    # locate latitde insertion point using same method 
    bi_lat_index = bi.bisect(cm_xarray.lat, y)
    
    if bi_lat_index == len(cm_xarray.lat):
        bi_lat_index -= 1
    
    # return x1, x2, y1, y2
    return {'x1': cm_xarray.lon.values[bi_lon_index - 1],
            'x2': cm_xarray.lon.values[bi_lon_index],
            'y1': cm_xarray.lat.values[bi_lat_index - 1],
            'y2': cm_xarray.lat.values[bi_lat_index]}

# testing functions 
q_test = find_q_coords(1, 85, data_xarray)
q_test        

# seeing if the built in function works the same 
test_xarray = data_xarray.isel(time = slice(0,4))

test_interp = bilinear_interpolation(1, 85, test_xarray) 
test_interp
test_interp_function = test_xarray.TREFHT_ANN.interp(lon=[1], lat =[85], method = "linear")
test_interp_function


