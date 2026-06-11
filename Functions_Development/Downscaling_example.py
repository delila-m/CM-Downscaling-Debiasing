# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 12:01:39 2026

@author: delil
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import random

# ---------- Load Simulated and Observed Data ----------

    # iTRACE
sim_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/atm-surface/itrace.11Ka-0Ka.atm.TREFHT.nc")

    # ERA5  
obs_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1950_present_az.nc")
obsp = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1940_1950_az.nc")



# ---------- Prepare ERA5 and iTrace for Interpolation ---------

    # convert itrace data to the same range as era5 (-180 to 180) & same spatial extent 
sim_same_latlon = sim_xarray.assign_coords(lon=(((sim_xarray.lon + 180) % 360) - 180)).sortby('lon')

    # find the lat & lon extent from era5 
lat_min_obs, lat_max_obs = obsp.latitude.min().item(), obsp.latitude.max().item()
lon_min_obs, lon_max_obs = obsp.longitude.min().item(), obsp.longitude.max().item()

    # trim itrace to same spatial extent as era5
sim_trimmed = sim_same_latlon.sel(
    lat=slice(lat_min_obs, lat_max_obs), 
    lon=slice(lon_min_obs, lon_max_obs)) 

    # define decades for decadal weighted average of era5 data
obsp.coords['decade'] = (obsp.valid_time.dt.year // 10) * 10

    # define weights 
weights = obsp.valid_time.dt.days_in_month

    # calculate the weighted mean 
weighted_temp = (obsp[['t2m']] * weights).groupby('decade').sum(dim='valid_time')
total_days = weights.groupby('decade').sum(dim='valid_time')

decadal_avg = weighted_temp / total_days

# =============================================================================
# 
# lats = np.array([33.33, 34.33, 35.33])
# lons = np.array([-111.33, -112.33, -113.33])
# 
# np.random.seed(123) 
# dummy_data = np.random.uniform(low = 220, high = 255, size = (3, 3))
# dummy_data
# 
# test_points = xr.DataArray(
#     data = dummy_data,
#     dims = ["lat", "lon"],
#     coords = {
#         "lat": ("lat", lats, {"long_name": "Latitude (North)", "units": "degrees_north"}),
#         "lon": ("lon", lons, {"long_name": "Longitude (East)", "units": "degrees_east"}),
#         },
#     name = "temperature",
#     attrs = {"long_name": "2m Temperature", "units": "Kelvin"})
#     
# print(test_points)
# =============================================================================



# ---------- Interpolation ----------

    # check difference between lat/lon extents of itrace (sim) and era5 (obs)
sim_trimmed.lat.min().item(), sim_trimmed.lat.max().item() #(33.157894736842096, 36.94736842105263)
sim_trimmed.lon.min().item(), sim_trimmed.lon.max().item() #(-112.5, -110.0)

lat_min_obs, lat_max_obs #(32.0, 37.0)
lon_min_obs, lon_max_obs #(-114.0, -109.0)
    """ because era5 has larger spatial extent,
        we need to extrapolate the edges of itrace for the grids to be equal """

sim_interpolated = sim_trimmed.interp(
    lat=decadal_avg.latitude, 
    lon=decadal_avg.longitude, 
    method='linear',
    kwargs={"fill_value": "extrapolate"} # This fills the edges that the model misses
)

    # check the lat/lon extent match 
print(sim_interpolated)
print(decadal_avg)


# ---------- Defining Datasets for Bias Correction ---------- 

    # break into historical and present sets for comparison with observed data
simp_interpolated = sim_interpolated.isel(time = slice(1099,1100)) # 1945
simh_interpolated = sim_interpolated.isel(time = slice(0,1099)) # 1935 to 10995 years bp
    # There is only one year of overlap between era5 and itrace 
obsp = decadal_avg.sel(decade = 1940, method = "nearest")


# ---------- Bias Correction ----------

def additive_bc(sim_base, sim_ref, obs_ref, 
                base_var, sim_ref_var, obs_ref_var):
    
    # making it work for the one year of data.. 
        # this step likely won't need to be used in the final function with monthly data 
    sim_ref_spatial = sim_ref[sim_ref_var].squeeze('time', drop=True)
    
    
    # find the difference between these two measurements 
    delta = obs_ref[obs_ref_var] - sim_ref_spatial
    #print(f"Calculated Delta: {delta.values}")
    
    new_var_name = "bc_" + base_var
    corrected_data = sim_base.assign({new_var_name: sim_base[base_var] + delta})
    
    return corrected_data
    
# with interpolated values    
additive_interp_test = additive_bc(simh_interpolated, simp_interpolated, obsp, "TREFHT_ANN", "TREFHT_ANN", "t2m")  
print(additive_interp_test.bc_TREFHT_ANN)
additive_interp_test.isnull().sum()

# check to see if points have been changed by delta
additive_interp_test.bc_TREFHT_ANN - simh_interpolated.TREFHT_ANN # prints all of the deltas for each gridcell 














# ---------- Visualizing NA values in interpolated set ----------

# selecting variable to plot 
data_to_plot = sim_interpolated_final['TREFHT_ANN'].isel(time=0) 

# create a mask for NaN values
is_nan = data_to_plot.isnull()

plt.figure(figsize=(10, 6))

# Plot the original data
data_to_plot.plot(cmap='viridis', add_colorbar=True, label='Original Data')

# Plot the NaN (interpolated) areas in a contrasting color (e.g., Red)
is_nan.where(is_nan).plot(add_colorbar=False, cmap='Reds', alpha=0.5, label='NaN / Interpolated')

plt.title('Original Data vs Interpolated NaN Points')
plt.show()


# ---------- Interppolation before Bias Correction Plot ----------

# selecting variable to plot 
data_to_plot = additive_interp_test['bc_TREFHT_ANN'].isel(time=0) 

# create a mask for NaN values
is_nan = data_to_plot.isnull()

plt.figure(figsize=(10, 6))

# Plot the original data
data_to_plot.plot(cmap='viridis', add_colorbar=True, label='Original Data')

# Plot the NaN (interpolated) areas in a contrasting color (e.g., Red)
is_nan.where(is_nan).plot(add_colorbar=False, cmap='Reds', alpha=0.5, label='NaN / Interpolated')

plt.title('Interppolation before Bias Correction with NaN Points')
plt.show()










# ---------- Bias Correction Before Interpolation Sample and Plot ----------

# Or bias correct first and interpolate after 
additive_test = additive_bc(simh, simp, obsp, "TREFHT_ANN", "TREFHT_ANN", "t2m")  
print(additive_interp_test)
additive_test.isnull().sum()

bc_interpolate = additive_test.interp(
    lat=test_points.lat, 
    lon=test_points.lon, 
    method='linear')
print(bc_interpolate)

bc_interpolate_expanded = bc_interpolate.reindex(lat=new_lat, lon=new_lon)

    # combine the two datasets     
bc_interpolate_final = bc_interpolate_expanded.combine_first(sim_interpolated)
bc_interpolate_final.isnull().sum()

# selecting variable to plot 
data_to_plot = bc_interpolate_final['TREFHT_ANN'].isel(time=0) 

# create a mask for NaN values
is_nan = data_to_plot.isnull()

plt.figure(figsize=(10, 6))

# Plot the original data
data_to_plot.plot(cmap='viridis', add_colorbar=True, label='Original Data')

# Plot the NaN (interpolated) areas in a contrasting color (e.g., Red)
is_nan.where(is_nan).plot(add_colorbar=False, cmap='Reds', alpha=0.5, label='NaN / Interpolated')

plt.title('Bias Correction Before Interpolation with NaN Points')
plt.show()




