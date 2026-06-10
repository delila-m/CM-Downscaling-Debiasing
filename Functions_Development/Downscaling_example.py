# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 12:01:39 2026

@author: delil
"""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import random

# ---------- Load Simulated and Observed Data ----------

    # iTRACE
sim_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/atm-surface/itrace.11Ka-0Ka.atm.TREFHT.nc")

    # ERA5  
obs_xarray = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1950_present_az.nc")
obsp = xr.open_dataset("C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/era5_monthly_temp_1940_1950_az.nc")

    # convert itrace data to the same range as era5 (-180 to 180) & same spatial extent 
sim_same_latlon = sim_xarray.assign_coords(lon=(((sim_xarray.lon + 180) % 360) - 180)).sortby('lon')
lat_min, lat_max = obsp.latitude.min().item(), obsp.latitude.max().item()
lon_min, lon_max = obsp.longitude.min().item(), obsp.longitude.max().item()

    # trim itrace to same spatial extent as era5
sim_mod = sim_same_latlon.sel(
    lat=slice(lat_min, lat_max), 
    lon=slice(lon_min, lon_max)) 


# ---------- Sample Interpolation Points ---------

lats = np.array([33.33, 34.33, 35.33])
lons = np.array([-111.33, -112.33, -113.33])

np.random.seed(123) 
dummy_data = np.random.uniform(low = 220, high = 255, size = (3, 3))
dummy_data

test_points = xr.DataArray(
    data = dummy_data,
    dims = ["lat", "lon"],
    coords = {
        "lat": ("lat", lats, {"long_name": "Latitude (North)", "units": "degrees_north"}),
        "lon": ("lon", lons, {"long_name": "Longitude (East)", "units": "degrees_east"}),
        },
    name = "temperature",
    attrs = {"long_name": "2m Temperature", "units": "Kelvin"})
    
print(test_points)

# ---------- Interpolation ----------

sim_interpolated = sim_mod.interp(
    lat=test_points.lat, 
    lon=test_points.lon, 
    method='linear')
print(sim_interpolated)

# ---------- Combine interpolated vlaues with Original set ----------
# NOTE this creates na values where the two datasets don't align 

    # create expanded coordinate lists including new interpolated points 
new_lat = np.sort(np.unique(np.concatenate([sim_mod.lat.values, sim_interpolated.lat.values])))
new_lon = np.sort(np.unique(np.concatenate([sim_mod.lon.values, sim_interpolated.lon.values])))

    # reindex ordidnal dataset to new dimensions including interpolated points 
sim_mod_expanded = sim_mod.reindex(lat=new_lat, lon=new_lon)

    # combine the two datasets     
sim_interpolated_final = sim_mod_expanded.combine_first(sim_interpolated)
sim_interpolated_final.isnull().sum()


# ---------- Defining Datasets for Bias Correction ---------- 

    # break into historical and present sets for comparison with observed data
simp_interpolated = sim_interpolated_final.isel(time = slice(1099,1100)) # 1945
simh_interpolated = sim_interpolated_final.isel(time = slice(0,1099)) # 1935 to 10995 years bp
    # There is only one year of overlap between era5 and itrace 
obsp = obsp.sel(valid_time = "1945")

    # or break into sets without interpolated values 
simp = sim_mod.isel(time = slice(1099,1100)) # 1945
simh = sim_mod.isel(time = slice(0,1099)) # 1935 to 10995 years bp


# ---------- Bias Correction ----------

def additive_bc(sim_base, sim_ref, obs_ref, 
                base_var, sim_ref_var, obs_ref_var):
    
    # take the average of your simulated and observed reference climate
    sim_mean = sim_ref[sim_ref_var].mean()
    obs_mean = obs_ref[obs_ref_var].mean()
    
    # find the difference between these two measurements 
    delta = obs_mean - sim_mean
    print(f"Calculated Delta: {delta.values}")
    
    new_var_name = "bc_" + base_var
    corrected_data = sim_base.assign({new_var_name: sim_base[base_var] + delta})
    
    return corrected_data
    
# with interpolated values    
additive_interp_test = additive_bc(simh_interpolated, simp_interpolated, obsp, "TREFHT_ANN", "TREFHT_ANN", "t2m")  
print(additive_interp_test)

additive_interp_test.isnull().sum()













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



# ---------- Bias Correction Before Interpolation ----------

# selecting variable to plot 
data_to_plot = additive_interp_test['TREFHT_ANN'].isel(time=0) 

# create a mask for NaN values
is_nan = data_to_plot.isnull()

plt.figure(figsize=(10, 6))

# Plot the original data
data_to_plot.plot(cmap='viridis', add_colorbar=True, label='Original Data')

# Plot the NaN (interpolated) areas in a contrasting color (e.g., Red)
is_nan.where(is_nan).plot(add_colorbar=False, cmap='Reds', alpha=0.5, label='NaN / Interpolated')

plt.title('Bias Correction Before Interpolation with NaN Points')
plt.show()











# ---------- Interppolation before Bias Correction ----------

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




