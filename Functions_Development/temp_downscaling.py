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
import cmethods as cm
import statistics as sta
import pandas as pd
import datetime as dt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


# Load the iTRACE
sim_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/atm-surface/itrace.11Ka-0Ka.atm.TREFHT.nc")

# opening observed dataset 
obs_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1950_present_az.nc")
obsp = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1940_1950_az.nc")


sim_xarray.time

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
    if not cm_xarray.lon.values[0] <= x <= cm_xarray.lon.values[len(cm_xarray.lon)-1]:
        print(f"Invalid Longitude. {x} Outside of range")
        return np.nan
    if not cm_xarray.lat.values[0] <= y <= cm_xarray.lat.values[len(cm_xarray.lat)-1]:
        print(f"Invalid Longitude. {y} Outside of range")
        return np.nan
    
    # locate longitude insertion point bounds using bisect
    bi_lon_index = bi.bisect(cm_xarray.lon, x) 
    
    # check to see if the index value is outside longitude range
    if bi_lon_index == len(cm_xarray.lon): 
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
q_test = find_q_coords(1, 85, sim_xarray)
q_test        

# seeing if the built in function works the same 
test_xarray = sim_xarray.isel(time = slice(0,4))

test_interp = bilinear_interpolation(1, 85, test_xarray) 
test_interp
test_interp_function = sim_xarray.TREFHT_ANN.interp(lon=[1], lat =[85], method = "linear")
test_interp_function



obs_xarray.valid_time.values
obs_xarray


test_bc = cm.adjust(
    method = "delta_method", 
    obs = decadal_avg["t2m"], 
    )

test_array = [1, 2, 1, 2, 3, 1, ]


# Bias correction (additive delta method) function 

# find the average for the projected and historical cm data

# find the difference between the two

# add the difference to the observed data




# function to create weighted average by day in month 
def weighted_average( data, type = "ANN" ): 
    # initialize variables 
    data['month'] = pd.to_datetime(data['valid_time']).month
    interm_value = int()
    weights_sum = int()
    
    # create weights for each month or season if calculating a seasonal average  
    match type:
        case "ANN":
            weights_dict = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
        case "MAM":
            weights_dict = {3:31, 4:30, 5:31}
        case "JJA":
            weights_dict = {6:30, 7:31, 8:31}
        case "SON":
            weights_dict = {9:30, 10:31, 11:30}
        case "DJF":
            weights_dict = {12:31, 1:31, 2:28}
        case _:
            print("Invalid average type")
            return np.nan
        
    # loop through the monthly values 
    for key in weights_dict:

        # multiply weights by monthly values 
        interm_values += data.t2m.values[key-1]*weights_dict[key]
        weights_sum += weights_dict[key]
        
    # return the weighted value 
    return(interm_values / weights_sum)


# define decades 
obs_xarray.coords['decade'] = (obs_xarray.valid_time.dt.year // 10) * 10

# define weights 
weights = obs_xarray.valid_time.dt.days_in_month

# calculate the weighted mean 
weighted_temp = (obs_xarray['t2m'] * weights).groupby('decade').sum(dim='valid_time')
total_days = weights.groupby('decade').sum(dim='valid_time')

decadal_avg = weighted_temp / total_days


# plotting mean and sd for era5 and itrace data 

# convert itrace data to the same range as era5 (-180 to 180)
model_mod = sim_xarray.assign_coords(lon=(((sim_xarray.lon + 180) % 360) - 180)).sortby('lon')

# define spatial extent 
lat_min, lat_max = decadal_avg.latitude.min().item(), decadal_avg.latitude.max().item()
lon_min, lon_max = decadal_avg.longitude.min().item(), decadal_avg.longitude.max().item()


# trim trace to same spatial extent as era5
    # brute forcing my way through this bc I can't deal with this shit
data_indexed = model_mod.sel(
    lat=slice(lat_min, lat_max), 
    lon=slice(lon_min, lon_max) 
)

simp = data_indexed.isel(time = slice(1098,1099))
simh = data_indexed.isel(time = slice(0,1098))


# interpolate model data to match grid of observed data 
data_interpolated = data_trimmed.interp(
    lat=decadal_avg.latitude, 
    lon=decadal_avg.longitude, 
    method='linear',
    kwargs={"fill_value": "extrapolate"} # This fills the edges that the model misses
)

obs_mean = decadal_avg.mean(dim='decade')
obs_std = decadal_avg.std(dim='decade')

mod_mean = data_interpolated['TREFHT_ANN'].mean(dim='time')
mod_std = data_interpolated['TREFHT_ANN'].std(dim='time')

fig, axes = plt.subplots(2, 2, figsize=(14, 10), 
                         subplot_kw={'projection': ccrs.PlateCarree()})

# Helper list for easier iteration
plots = [
    (obs_mean, 'Observation Mean', 'viridis'),
    (mod_mean, 'Model Mean', 'viridis'),
    (obs_std, 'Observation SD', 'plasma'),
    (mod_std, 'Model SD', 'plasma')
]

for i, (data, title, cmap) in enumerate(plots):
    ax = axes.flatten()[i]
    
    # Plot data
    # Note: we use 'latitude'/'longitude' for obs and 'lat'/'lon' for model
    if 'latitude' in data.coords:
        p = data.plot(ax=ax, transform=ccrs.PlateCarree(), cmap=cmap, add_colorbar=False)
    else:
        p = data.plot(ax=ax, x='lon', y='lat', transform=ccrs.PlateCarree(), cmap=cmap, add_colorbar=False)
    
    # Add map features
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=0.5)
    
    # Formatting
    ax.set_title(title, fontsize=14)
    fig.colorbar(p, ax=ax, orientation='vertical', label='Temperature (K)', shrink=0.8)
    
    # Set the specific extent
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())

plt.tight_layout()
plt.show()


import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches

fig = plt.figure(figsize=(10, 8))
ax = plt.axes(projection=ccrs.PlateCarree())

# 3. Add the "Shapefile" data via Cartopy features
# This pulls the 1:50m resolution state boundaries
states_provinces = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_1_states_provinces_lines',
    scale='50m',
    facecolor='none'
)

# Add land/ocean for a clean look
ax.add_feature(cfeature.LAND, facecolor='#f9f9f9')
ax.add_feature(cfeature.BORDERS, linestyle=':')
ax.add_feature(states_provinces, edgecolor='black', linewidth=1)

# 4. Set the map window to show the whole state + padding
# [lon_start, lon_end, lat_start, lat_end]
ax.set_extent([-116, -108, 30.5, 38.5], crs=ccrs.PlateCarree())

# 5. Add the highlighted box
width = lon_max - lon_min
height = lat_max - lat_min
rect = mpatches.Rectangle(
    (lon_min, lat_min), width, height,
    linewidth=2, edgecolor='red', facecolor='red', alpha=0.3,
    transform=ccrs.PlateCarree())
ax.add_patch(rect)

# 6. Add gridlines with coordinate labels
gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
gl.top_labels = False
gl.right_labels = False








