# -*- coding: utf-8 -*-
"""
Created on Thu Apr  2 14:14:21 2026

@author: delil
"""

# Load libraries
import numpy as np
import xarray as xr
import bisect as bi

# Load the iTRACE
data_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/atm-surface/itrace.11Ka-0Ka.atm.TREFHT.nc")



# bilinear interpolation function arguments:
    # coordinates for point to be interpolated
    # climate model data as an xarray object
        # would it be worthwhile to pass attribute names??
def bilinear_interpolation( x, y, cm_xarray ):
    
    # find nearest coords to desired interpolation point 
    q_coords = find_q_coords(x, y, cm_xarray)
    
    # initialize list to store interpolated values 
    temp
    # loop through time in array
    
        # grab data values for Q11, Q12, Q21, Q22 using given coordinates 
        
        # calculate R1 & R1
        
        # calculate P (interpolated point)
    
        # add to array


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
    
    # return coordinates of Q11, Q12, Q21, Q22
    return {'q11': [cm_xarray.lon.values[bi_lon_index - 1], cm_xarray.lat.values[bi_lat_index - 1]],
            'q12': [cm_xarray.lon.values[bi_lon_index - 1], cm_xarray.lat.values[bi_lat_index]],
            'q21': [cm_xarray.lon.values[bi_lon_index], cm_xarray.lat.values[bi_lat_index - 1]],
            'q22': [cm_xarray.lon.values[bi_lon_index], cm_xarray.lat.values[bi_lat_index]]}

q_test = find_q_coords(1, 91, data_xarray)
q_test        
    
    
    
    
    




















