#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  4 21:49:29 2023

@author: polinarozhkova
"""

# Timeframe
# compare 2019 and 2021?

# Vars:
# race, number of pharmacies, number of/concentration of providers,
# % of pop with vehicle

# Sources:
# Clinics (manually collected) - https://www.methadonecenters.com/directory/illinois/chicago/
# Opioid Treatment Programs (89 in IL) - https://dpt2.samhsa.gov/treatment/
# Buprenorphine Practitioner Locator - https://www.samhsa.gov/medication-assisted-treatment/find-treatment/treatment-practitioner-locator?field_bup_lat_lon_proximity%5Bvalue%5D=25&field_bup_lat_lon_proximity%5Bsource_configuration%5D%5Borigin_address%5D=&field_bup_city_value=&field_bup_state_value=17&order=field_bup_city&sort=asc&page=3
# Medical Examiner Opioid Related Deaths - https://datacatalog.cookcountyil.gov/Public-Safety/Medical-Examiner-Case-Archive/cjeq-bs86/data

import os
import numpy as np
from sodapy import Socrata
import pandas as pd
import geopandas
# from shapely.geometry import Point, Polygon
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from shapely import wkt

# RENAME path wherever you save the original data
path = r'/Users/polinarozhkova/Desktop/GitHub/moud_access/'

area_shp = os.path.join(path, 'inputs/Boundaries - Community Areas (current)',
                        'geo_export_122237a7-de0c-463d-b81f-e6d53bf2e92a.shp')
c_area = geopandas.read_file(area_shp)
client = Socrata("datacatalog.cookcountyil.gov", None)
results = client.get_all('cjeq-bs86', opioids=True, limit=10000)
chicago_opioid = pd.DataFrame.from_records(results)
chicago_opioid.to_csv('inputs/medical_examiner_opioid.csv', index=False)
pharmacy = pd.read_csv(os.path.join(path, 'inputs/Pharmacy_Status.csv'))
bupren = pd.read_csv(os.path.join(path, 'inputs/locator_export.csv'))
demograph = pd.read_excel(
    (os.path.join(path, 'inputs/heartland_alliance_community_data.xlsx')),
    sheet_name=1)


# use this to impute community area names to locations of bupren providers
area_dict = dict(zip(c_area.community, c_area.geometry))


# Cleaning, filtering, joining to shapefiles
bupren = bupren[(bupren['county'] == 'COOK') &
                ((bupren['city'] == 'Chicago')
                 | (bupren['city'] == 'CHICAGO'))]
bupren_gdf = geopandas.GeoDataFrame(
    bupren, geometry=geopandas.points_from_xy(bupren.longitude,
                                              bupren.latitude))

c_bupren_join = geopandas.sjoin(c_area, bupren_gdf,
                                how="inner", op='intersects')

c_bupren_join = geopandas.GeoDataFrame(
    c_bupren_join, geometry=geopandas.points_from_xy(c_bupren_join.longitude,
                                                     c_bupren_join.latitude))

bupren_area = pd.DataFrame(c_bupren_join.groupby(
     ['community'])['area'].count()).reset_index()

pharmacy['point_geo'] = pharmacy['New Georeferenced Column'
                                 ].dropna().astype(str).apply(wkt.loads)
pharmacy_gdf = geopandas.GeoDataFrame(pharmacy, geometry='point_geo')

c_pharmacy_join = geopandas.sjoin(c_area, pharmacy_gdf,
                                  how="inner", op='intersects')

pharmacy_area = pd.DataFrame(c_pharmacy_join.groupby(
     ['community'])['area'].count()).reset_index()

# opioid related deaths by community area 2019, 2020, 2021
opioid_df = chicago_opioid[['casenumber', 'death_date', 'age', 'gender',
                            'race', 'latino', 'manner', 'primarycause',
                            'gunrelated', 'opioids', 'incident_street',
                            'incident_city', 'incident_zip', 'longitude',
                            'latitude', 'location', 'chi_commarea']]


opioid_df['death_date'] = pd.to_datetime(opioid_df['death_date'])

opioid_df = opioid_df[(opioid_df['death_date'].dt.year > 2018) & (
    opioid_df['death_date'].dt.year < 2022)]

opioid_df = opioid_df[(opioid_df['incident_city'] == 'CHICAGO')]

opioid_df = opioid_df.rename(columns={'chi_commarea': 'community'})

print(opioid_df.shape)
print(opioid_df.isna().sum())

# drop suicicdes, homicides, undetermined
opioid_df = opioid_df[(opioid_df['manner'] == 'ACCIDENT') |
                      (opioid_df['manner'] == 'NATURAL')]

# dropping 227 incidents where we don't have a location
opioid_df = opioid_df.dropna(subset=['location'])

# have to convert strings to dummies or categorical variables as integers
opioid_df = opioid_df.join(pd.get_dummies(
    opioid_df[['gender', 'race', 'manner']]))


opioid_shp = c_area.merge(opioid_df, on=['community'])

opioid_2019 = opioid_shp[(opioid_shp['death_date'].dt.year == 2019)]

opioid_2020 = opioid_shp[(opioid_shp['death_date'].dt.year == 2020)]

opioid_2021 = opioid_shp[(opioid_shp['death_date'].dt.year == 2021)]

# # number of deaths by community areas
# # merge this with demographic vars
opioid_2019_grouped = pd.DataFrame(opioid_2019.groupby(
     ['community'])['casenumber'].count()).reset_index()
opioid_2020_grouped = pd.DataFrame(opioid_2020.groupby(
     ['community'])['casenumber'].count()).reset_index()
opioid_2021_grouped = pd.DataFrame(opioid_2021.groupby(
     ['community'])['casenumber'].count()).reset_index()

test = c_area.merge(opioid_2019_grouped, how='outer').rename({'casenumber': 'num_od_2019'})

# pharmacy = pharmacy.rename(columns={'New Georeferenced Column': 'point_obect'})
# pharmacy_gdf = geopandas.GeoDataFrame(data=pharmacy, geometry=pharmacy['point_object'], crs=4329)
# pharmacy['longitude'] = pharmacy['point_object'].apply(lambda p: p.x)