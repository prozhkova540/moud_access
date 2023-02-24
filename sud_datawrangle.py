#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 23 17:51:04 2023
@author: polinarozhkova
"""

# Sources:
# Clinics (manually collected) - https://www.methadonecenters.com/directory/illinois/chicago/
# Opioid Treatment Programs (89 in IL) - https://dpt2.samhsa.gov/treatment/
# Buprenorphine Practitioner Locator - https://www.samhsa.gov/medication-assisted-treatment/find-treatment/treatment-practitioner-locator?field_bup_lat_lon_proximity%5Bvalue%5D=25&field_bup_lat_lon_proximity%5Bsource_configuration%5D%5Borigin_address%5D=&field_bup_city_value=&field_bup_state_value=17&order=field_bup_city&sort=asc&page=3
# Medical Examiner Opioid Related Deaths - https://datacatalog.cookcountyil.gov/Public-Safety/Medical-Examiner-Case-Archive/cjeq-bs86/data


from sodapy import Socrata
import pandas as pd
import os


path = r'//Users/polinarozhkova/Desktop/GitHub/moud_access/'
client = Socrata("datacatalog.cookcountyil.gov", None)


results = client.get_all('cjeq-bs86', opioids=True, limit=10000)
chicago_opioid = pd.DataFrame.from_records(results)
chicago_opioid.to_csv('inputs/medical_examiner_opioid.csv', index=False)


fname_1 = 'inputs/clinics.xlsx'
fname_2 = 'inputs/TreatmentProgram.xlsx'


clinics = pd.read_excel((os.path.join(path, fname_1)), sheet_name=1)
treatment = pd.read_excel((os.path.join(path, fname_2)), sheet_name=0)
#cdp_hom = pd.read_csv(os.path.join(path, fname_3))
#cdp_victims = pd.read_csv(os.path.join(path, fname_4))
