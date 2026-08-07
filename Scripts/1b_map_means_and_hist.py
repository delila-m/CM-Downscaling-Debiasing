#==============================================================================
# This script loads ERA5 and trace data, computes monthly means, and mokes some
# plots.
#==============================================================================

import numpy as np
import matplotlib.pyplot as plt
import xarray as xr



#%% LOAD DATA

# Load the ERA5 and TraCE-21k datasets
data_dir = "C:/Users/delil/Desktop/NAU/Research/CM Research 2026/CM-Downscaling-Debiasing/Data/"
xarray_era5  = xr.open_dataset(data_dir+"era5_1940-1990CE_monthly_temp_and_precip_smaller.nc")
xarray_trace = xr.open_dataset(data_dir+"trace_1940-1990CE_monthly_temp_and_precip.nc")


#%% MAP MEANS

# Compute means over years
xarray_era5_mean = xarray_era5.mean("year")
xarray_trace_mean = xarray_trace.mean("year")

# Map mean precipitation in January
month_selected = 7
f,ax = plt.subplots(2,1,figsize=(10,12))
xarray_era5_mean.precip.sel(month = month_selected).plot(vmin=0,  vmax=5, cmap="Blues", xlim=[-140,-50], ylim=[15,75], ax=ax[0])
xarray_trace_mean.precip.sel(month = month_selected).plot(vmin=0, vmax=5, cmap="Blues", xlim=[-140,-50], ylim=[15,75], ax=ax[1])


#%% PLOT HISTOGRAM

month_selected = 1
lat_selected = 38
lon_selected = -98

# Get precip values at the selected location and month
values_era5 = xarray_era5.precip.interp(lat = lat_selected, lon = lon_selected, method = 'linear').sel(month = month_selected)
values_trace = xarray_trace.precip.interp(lat = lat_selected, lon = lon_selected, method = 'linear').sel(month = month_selected)

# Print max values and specify histogram bins
print('Max values:')
print(np.nanmax(values_era5))
print(np.nanmax(values_trace))
bins = np.linspace(0,10,21)

# Map mean precipitation in January
f,ax1 = plt.subplots(1,1,figsize=(10,6))
ax1.hist(values_era5,bins=bins,color='tab:blue',alpha=0.5,label='era5')
ax1.hist(values_trace,bins=bins,color='tab:red',alpha=0.5,label='trace')
ax1.set_title('Monthly precipitation values for 1940-1990\nlat='+str(lat_selected)+', lon='+str(lon_selected)+', month='+str(month_selected))
ax1.set_xlabel('Precip (mm/day)')
ax1.set_ylabel('Frequency')
ax1.legend()
plt.show()



