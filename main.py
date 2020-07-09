# coding: utf-8
import datetime as dt
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr


def CGL():
  
    path = 'D:/Data/CGL_subproject_coarse_res/2019/300/c_gls_NDVI300_201905010000_GLOBE_PROBAV_V1.0.1.nc'

    head, tail = os.path.split(path)
    pos = [pos for pos, char in enumerate(tail) if char == '_'][2]
    date = tail[pos + 1: pos + 9]
    date_h = dt.datetime.strptime(date, '%Y%m%d').date()

    my_ext = [-18.58, 62.95, 51.57, 28.5]

    ds = xr.open_dataset(path, mask_and_scale=False)

    da_rmse = None
    if 'LAI' in ds.data_vars:
        param = {'product': 'LAI',
                 'short_name': 'leaf_area_index',
                 'long_name': 'Leaf Area Index Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 7,
                 'DIGITAL_MAX': 210,
                 'SCALING': 1./30,
                 'OFFSET': 0}
        da = ds.LAI

    elif 'FCOVER' in ds.data_vars:
        param = {'product': 'FCOVER',
                 'short_name': 'vegetation_area_fraction',
                 'long_name': 'Fraction of green Vegetation Cover Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'valid_range': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 1.,
                 'DIGITAL_MAX': 250,
                 'SCALING': 1./250,
                 'OFFSET': 0}
        da = ds.FCOVER

    elif 'FAPAR' in ds.data_vars:
        param = {'product': 'FAPAR',
                 'short_name': 'Fraction_of_Absorbed_Photosynthetically_Active_Radiation',
                 'long_name': 'Fraction of Absorbed Photosynthetically Active Radiation Resampled 1 KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing',
                 'flag_values': '255',
                 'units': '',
                 'valid_range': '',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 0.94,
                 'DIGITAL_MAX': 235,
                 'SCALING': 1./250,
                 'OFFSET': 0}
        da = ds.FAPAR

    elif 'NDVI' in ds.data_vars:
        param = {'product': 'NDVI',
                 'short_name': 'Normalized_difference_vegetation_index',
                 'long_name': 'Normalized Difference Vegetation Index Resampled 1 Km',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'Missing cloud snow sea background',
                 'flag_values': '[251 252 253 254 255]',
                 'units': '',
                 'PHYSICAL_MIN': -0.08,
                 'PHYSICAL_MAX': 0.92,
                 'DIGITAL_MAX': 250,
                 'SCALING': 1./250,
                 'OFFSET': -0.08}
        da = ds.NDVI

    elif 'DMP' in ds.data_vars:
        param = {'product': 'DMP',
                 'short_name': 'dry_matter_productivity',
                 'long_name': 'Dry matter productivity Resampled 1KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'sea',
                 'flag_values': '-2',
                 'units': 'kg / ha / day',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 327.67,
                 'DIGITAL_MAX': 32767,
                 'SCALING': 1./100,
                 'OFFSET': 0}
        da = ds.DMP

    elif 'GDMP' in ds.data_vars:
        param = {'product': 'GDMP',
                 'short_name': 'Gross_dry_matter_productivity',
                 'long_name': 'Gross dry matter productivity Resampled 1KM',
                 'grid_mapping': 'crs',
                 'flag_meanings': 'sea',
                 'flag_values': '-2',
                 'units': 'kg / hectare / day',
                 'PHYSICAL_MIN': 0,
                 'PHYSICAL_MAX': 655.34,
                 'DIGITAL_MAX': 32767,
                 'SCALING': 1./50,
                 'OFFSET': 0}
        da = ds.GDMP

    else:
        sys.exit('GLC product not found please chek')

    def find_nearest(array, value):
        array = np.asarray(array)
        idx = (np.abs(array - value)).argmin()
        return array[idx]

    def bnd_box_adj(my_ext):
        lat_1k = np.arange(80., -60., -1. / 112)
        lon_1k = np.arange(-180., 180., 1. / 112)

        lat_300 = ds.lat.values
        lon_300 = ds.lon.values
        ext_1K = np.zeros(4)

        # TODO find a more pythonic way
        ext_1K[0] = find_nearest(lon_1k, my_ext[0]) - 1. / 224
        ext_1K[1] = find_nearest(lat_1k, my_ext[1]) + 1. / 224
        ext_1K[2] = find_nearest(lon_1k, my_ext[2]) - 1. / 224
        ext_1K[3] = find_nearest(lat_1k, my_ext[3]) + 1. / 224

        my_ext[0] = find_nearest(lat_300, ext_1K[0])
        my_ext[1] = find_nearest(lon_300, ext_1K[1])
        my_ext[2] = find_nearest(lat_300, ext_1K[2])
        my_ext[3] = find_nearest(lon_300, ext_1K[3])
        return my_ext

    if len(my_ext):
        assert my_ext[1] >= my_ext[3], 'min Latitude is bigger than correspond Max, ' \
                                       'pls change position or check values.'
        assert my_ext[0] <= my_ext[2], 'min Longitude is bigger than correspond Max, ' \
                                       'pls change position or check values.'
        assert ds.lat[-1] <= my_ext[3] <= ds.lat[0], 'min Latitudinal value out of original dataset Max ext.'
        assert ds.lat[-1] <= my_ext[1] <= ds.lat[0], 'Max Latitudinal value out of original dataset Max ext.'
        assert ds.lon[0] <= my_ext[0] <= ds.lon[-1], 'min Longitudinal value out of original dataset Max ext.'
        assert ds.lon[0] <= my_ext[2] <= ds.lon[-1], 'Max Longitudinal value out of original dataset Max ext.'
        adj_ext = bnd_box_adj(my_ext)

        da = da.sel(lon=slice(adj_ext[0], adj_ext[2]), lat=slice(adj_ext[1], adj_ext[3]))
    else:
        da = da.shift(lat=1, lon=1)

    # TODO differentiate according to the different products structures
    da_msk = da.where(da <= param['DIGITAL_MAX'])

    coarsen = da_msk.coarsen(lat=3, lon=3, coord_func=np.mean, boundary='trim', keep_attrs=False).mean()

    vo = xr.where(da <= param['DIGITAL_MAX'], 1, 0)
    vo_cnt = vo.coarsen(lat=3, lon=3, coord_func=np.mean, boundary='trim', keep_attrs=False).sum()
    da_r = coarsen.where(vo_cnt >= 5)

    da_r.name = param['product']
    da_r.attrs['short_name'] = param['short_name']
    da_r.attrs['long_name'] = param['long_name']
    prmts = dict({param['product']: {'dtype': 'f8', 'zlib': 'True', 'complevel': 4}})
    name = param['product']
    da_r.to_netcdf(rf'D:/Data/CGL_subproject_coarse_res/Tests/CGLS_{name}_1KM_R_Europe_{date}.nc', encoding=prmts)
    print('Done')

    da_r.plot(robust=True, cmap='YlGn', figsize=(15, 10))

    plt.title(f'Copernicus Global Land\n Resampled {name} to 1K over Europe\n date: {date_h}')
    plt.ylabel('latitude')
    plt.xlabel('longitude')
    plt.draw()
    plt.show()


if __name__ == '__main__':
    CGL()
