#==============================================================================
# Exploring precipitation relationships between trace and era5.
#    author: Michael Erb
#==============================================================================

import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr


#%% LOAD DATA

# Load the trace and ERA5 data
data_dir = "C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/"


xarray_data = xr.open_dataset(data_dir+'trace_and_era5_1940-1990CE_monthly_precip.nc')
lat = xarray_data.lat.values
lon = xarray_data.lon.values


#%% MAP MEANS

# Compute means over years
xarray_data_mean = xarray_data.mean("year")

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

#%% EXPLORE PRECIP RELATIONSHIPS

# Make a figure comparing precipitation at locations
def compare_precip(month_selected,lat_selected,lon_selected):
    #
    # Get precip values at the selected location and month
    values_era5 = xarray_data.precip_era5.interp(lat = lat_selected, lon = lon_selected, method = 'nearest').sel(month = month_selected).values
    values_trace = xarray_data.precip_trace.interp(lat = lat_selected, lon = lon_selected, method = 'nearest').sel(month = month_selected).values
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
