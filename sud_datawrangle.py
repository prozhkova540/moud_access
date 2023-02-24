#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 17:51:04 2023
@author: polinarozhkova
"""

# Timeframe
# compare 2019 and 2021?

#
# Vars
# majority race, number of pharmacies, number of/concentration of providers,

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
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable


path = r'//Users/polinarozhkova/Desktop/GitHub/moud_access/'


area_shp = os.path.join(path, 'Boundaries - Community Areas (current)',
                        'geo_export_122237a7-de0c-463d-b81f-e6d53bf2e92a.shp')
community_area = geopandas.read_file(area_shp)


client = Socrata("datacatalog.cookcountyil.gov", None)
results = client.get_all('cjeq-bs86', opioids=True, limit=10000)
chicago_opioid = pd.DataFrame.from_records(results)
chicago_opioid.to_csv('inputs/medical_examiner_opioid.csv', index=False)


clinics = pd.read_excel((os.path.join(path, 'inputs/clinics.xlsx')), sheet_name=1)
treatment = pd.read_excel((os.path.join(path, 'inputs/TreatmentProgram.xlsx')), sheet_name=0)
pharmacy = pd.read_csv(os.path.join(path, 'inputs/Pharmacy_Status.csv'))
bupren = pd.read_csv(os.path.join(path, 'inputs/locator_export.csv'))


# Cleaning and Filtering
bupren = bupren[(bupren['county'] == 'COOK') & ((bupren['city'] == 'Chicago')
                                                | (bupren['city'] == 'CHICAGO'))]
