# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 13:54:11 2026

@author: delil
"""

# %%
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import datetime as dt
import random
import cmethods as cm
import pandas as pd 
import cartopy.crs as ccrs


# %% ---------- Load Simulated and Observed Data ----------

data_dir = "C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/"

xarray_era5  = xr.open_dataset(data_dir+"era5_1940-1990CE_monthly_temp_and_precip_smaller.nc")
xarray_trace = xr.open_dataset(data_dir+"trace_1940-1990CE_monthly_temp_and_precip.nc")

xarray_trace_era5 = xr.open_dataset(data_dir+"trace_and_era5_1940-1990CE_monthly_precip.nc")
#xarray_trace_era5_1d_time = xr.open_dataset(data_dir+"trace_and_era5_1940-1990CE_monthly_precip_1d_time.nc")


# %% ---------- Prepare ERA5 and iTrace for Interpolation ---------

def stack_time(xarray_ds):
        # stack the year & month dimensions into a single dimension
    xarray_stacked = xarray_ds.stack(time=("year", "month"))
    
        # Create the continuous index starting from 1940-01-01
    time_index = pd.date_range(start=f"{xarray_trace_era5.year.values[0]}-{xarray_trace_era5.month.values[0]:02d}-01",
                               periods=xarray_trace_era5.sizes["year"] * xarray_trace_era5.sizes["month"],
                               freq="MS")
    
        # assign the new time index
    xarray_1d_time = (xarray_stacked
                      .drop_vars(["time", "year", "month"], errors="ignore")
                      .assign_coords(time=time_index))
    return xarray_1d_time


xarray_trace_era5_1d_time = stack_time(xarray_trace_era5)
xarray_trace_1d_time = stack_time(xarray_trace)
xarray_era5_1d_time = stack_time(xarray_era5)

xarray_era5_1d_time.isnull().sum() #0
xarray_trace_1d_time.isnull().sum() #0
xarray_trace_era5_1d_time.precip_era5.isnull().sum() #86904


# plt.contourf(xarray_trace_era5.precip_era5.values[0,0,:,:]) 

 # xarray_trace_era5_1d_time.precip_era5 ->  shape=(25, 48, 612)
 # xarray_trace_era5_1d_time.precip_trace -> shape=(25, 48, 612)
 # qdm_interpolated.precip ->                shape=(201, 281, 132)
 # qdm_result.precip ->                      shape=(25, 48, 132)
# %% ---------- Defining Datasets for Bias Correction ---------- 


# break into historical and present sets for comparison with observed data
xarray_historical = xarray_trace_era5_1d_time.sel(time = slice('1940-01-01', '1979-12-01')) 
xarray_present = xarray_trace_era5_1d_time.sel(time= slice('1980-01-01', '1990-12-01')) 


# %% ---------- Bias Correction ----------

obs = xarray_historical.precip_era5.rename("precip")
simh = xarray_historical.precip_trace.rename("precip")
simp = xarray_present.precip_trace.rename("precip")


qdm_result = cm.adjust(
    method="quantile_delta_mapping",
    obs=obs,
    simh=simh,
    simp=simp,
    n_quantiles=100,  
    kind="*",
)


qm_result = cm.adjust(
    method="quantile_mapping",
    obs=obs,
    simh=simh,
    simp=simp,
    n_quantiles=100,  
    kind="*",
)


# =============================================================================
# 
# # try month by month?
#  
# # initialize temp array to hold bias corrected data for each month 
# adjusted_months = []
#  
# # loop through each month 
# for m in range(1, 13):
#     # slice data for month in index
#     obs_m  = xarray_historical.precip_era5.sel(time=xarray_historical.time.dt.month == m)
#     simh_m = xarray_historical.precip_trace.sel(time=xarray_historical.time.dt.month == m)
#     simp_m = xarray_present.precip_trace.sel(time=xarray_present.time.dt.month == m)
#  
#     # Adjust for this specific month
#     res_m = cm.adjust(
#         method="quantile_delta_mapping",
#         obs=obs_m.rename("precip"),
#         simh=simh_m.rename("precip"),
#         simp=simp_m.rename("precip"),
#         n_quantiles=20,  
#         kind="*") # multiplicative delta scaling for percip- if we want to use qm for temperature we could use additive here 
#     adjusted_months.append(res_m)
# 
# # combine and sort along time
# qdm_m_result = xr.concat(adjusted_months, dim="time").sortby("time")
#  
# =============================================================================


# %% ---------- Interpolation ----------

qdm_interpolated = qdm_result.interp(
    lat=xarray_era5.lat, 
    lon=xarray_era5.lon, 
    method='linear',
    kwargs={"fill_value": "extrapolate"} # This fills the edges that the model misses
)

qm_interpolated = qm_result.interp(
    lat=xarray_era5.lat, 
    lon=xarray_era5.lon, 
    method='linear',
    kwargs={"fill_value": "extrapolate"} # This fills the edges that the model misses
)

qdm_interpolated.isnull().sum()

    # check the lat/lon extent match 
print(qdm_interpolated)
print(xarray_trace_1d_time)


# %% Visualize Bias Correction Results in maps 

# map means 

# Compute means over years
xarray_data_mean = xarray_trace_era5.mean("year")

# Make a map of monthly mean precipitation
month_selected = 7

def compare_maps(month_selected):
    #
    #
    #f,ax = plt.subplots(2,1,figsize=(10,12))
    #xarray_data_mean.precip_era5.sel(month = month_selected).plot(vmin=0,  vmax=5, cmap="Blues", xlim=[-140,-50], ylim=[15,75], ax=ax[0])
    #xarray_data_mean.precip_trace.sel(month = month_selected).plot(vmin=0, vmax=5, cmap="Blues", xlim=[-140,-50], ylim=[15,75], ax=ax[1])
    #plt.coastlines(ax=ax[0])
    #
    # Get values
    map_era5 = xarray_data_mean.precip_era5.sel(month = month_selected)
    map_trace = xarray_data_mean.precip_trace.sel(month = month_selected)
    #
    # Make a map
    plt.figure(figsize=(16,8))
    ax1 = plt.subplot2grid((1,2),(0,0),projection=ccrs.LambertConformal(central_longitude=-100)); ax1.set_extent([-140,-60,10,76],ccrs.PlateCarree())
    ax2 = plt.subplot2grid((1,2),(0,1),projection=ccrs.LambertConformal(central_longitude=-100)); ax2.set_extent([-140,-60,10,76],ccrs.PlateCarree())
    #
    map1 = ax1.contourf(lon,lat,map_era5,np.arange(0,10.1,1),cmap='Blues',extend='both',transform=ccrs.PlateCarree())
    plt.colorbar(map1,orientation='horizontal',ax=ax1,fraction=0.08,pad=0.02)
    ax1.set_title('ERA5 precipitation for month '+str(month_selected),loc='center',fontsize=18)
    ax1.coastlines()
    #
    map2 = ax2.contourf(lon,lat,map_trace,np.arange(0,10.1,1),cmap='Blues',extend='both',transform=ccrs.PlateCarree())
    plt.colorbar(map2,orientation='horizontal',ax=ax2,fraction=0.08,pad=0.02)
    ax2.set_title('TraCE-21ka precipitation for month '+str(month_selected),loc='center',fontsize=18)
    ax2.coastlines()
    #
    plt.show()

for month_selected in np.arange(1,13):
    compare_maps(month_selected)
    

# %% visualize bias correction results 


# Make a figure comparing precipitation at locations
def compare_precip(month_selected,lat_selected,lon_selected):
    #
    # Get precip values at the selected location and month
    era5_interp = xarray_present.precip_era5.interp(lat = lat_selected, lon = lon_selected, method = 'nearest')
    trace_interp = qm_interpolated.precip.interp(lat = lat_selected, lon = lon_selected, method = 'nearest')
    
    values_era5 = era5_interp.sel(time = (era5_interp.time.dt.month == month_selected)).values
    values_trace = trace_interp.sel(time = (trace_interp.time.dt.month == month_selected)).values
    #
    # Make a plot
    f,ax = plt.subplots(1,2,figsize=(13,6))
    max_value = np.max([np.max(values_trace),np.max(values_era5)])+0.1
    #
    # Histogram of precipitation
    bins = np.linspace(0,10,21)
    ax[0].hist(values_era5,bins=bins,color='tab:blue',alpha=0.5,label='era5')
    ax[0].hist(values_trace,bins=bins,color='tab:red',alpha=0.5,label='trace')
    ax[0].set_title('Monthly precipitation values for 1940-1990\nlat='+str(lat_selected)+', lon='+str(lon_selected)+', month='+str(month_selected))
    ax[0].set_xlabel('Precip (mm/day)')
    ax[0].set_ylabel('Frequency')
    ax[0].legend()
    #
    # Scatterplot comparing sorted precipitation
    ax[1].scatter(np.sort(values_trace),np.sort(values_era5))
    ax[1].plot([0,max_value],[0,max_value],c='gray',linestyle='--')
    ax[1].set_xlim(0,max_value)
    ax[1].set_ylim(0,max_value)
    ax[1].set_title('Monthly precipitation values for 1940-1990\nlat='+str(lat_selected)+', lon='+str(lon_selected)+', month='+str(month_selected))
    ax[1].set_xlabel('TraCE-21k')
    ax[1].set_ylabel('ERA5')
    ax[1].set_box_aspect(1)
    plt.show()

lat_selected = 38
lon_selected = -98
compare_precip(1,lat_selected,lon_selected)
compare_precip(6,lat_selected,lon_selected)
compare_precip(10,lat_selected,lon_selected)


# %%

plt.figure(figsize=(10,5),dpi=216)
simh.groupby("time.month").mean(...).plot(label="Trace_H (1/1940-12/1979)")
simp.groupby("time.month").mean(...).plot(label="Trace_P (1/1980-12/1990)")
obs.groupby("time.month").mean(...).plot(label="ERA5 (1/1940-12/1979")
qm_result.precip.groupby("time.month").mean(...).plot(label="BC (1/1980-12/1990)$")
qm_interpolated.precip.groupby("time.month").mean(...).plot(label="BC_Interp (1/1980-12/1990)$")
plt.title("Historical, modeled, and adjusted temperatures")
plt.xlim(0,12)
plt.gca().grid(alpha=.3)
plt.legend();
















