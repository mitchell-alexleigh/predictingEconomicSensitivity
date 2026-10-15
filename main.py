#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  2 22:17:27 2026

@author: alex
"""
import pandas as pd
from dataProcessing import *
from pathlib import Path


# Perpare raw files from each data 
### handle hierarchies in US census data to retun one record per year per county per original file
ucdc_level_runner('EducationAttainment','Total','Estimate')
ucdc_runner('MedianMonthlyCostDollars','Estimate')
ucdc_runner('OccupancyStatus','Estimate') 
#extract single measure at a time for occupation data and store each in seprate csv until final data set 
ucdc_level_runner('OccupationByIndustry','Total','Estimate')
ucdc_level_runner('OccupationByIndustry','Management','Estimate')
ucdc_level_runner('OccupationByIndustry','Service','Estimate')
ucdc_level_runner('OccupationByIndustry','Sales','Estimate')
ucdc_level_runner('OccupationByIndustry','Natural','Estimate')
ucdc_level_runner('OccupationByIndustry','Production','Estimate')
ucdc_runner('MeansTransportation','Estimate')
ucdc_runner('MonthlyGasCost','Estimate')
ucdc_runner('MonthlyElectricCost','Estimate')
ucdc_runner('MonthlyCostPercent','Estimate')

### pre excel files retruning csv files containing one record per year per county per original file
FIPS_runner('PovertyAndMedianIncome', 4, 2024)
FIPS_runner('SnapBenafits',3,False)# all years already in file 
saipe_unpivot('SnapBenafits_cntysnap_cleaned.csv','SNAP','SnapBenafits')
FIPS_runner('LaborForce',2,False)
FIPS_runner('HousePriceIndex',6,False) # nothing needs to be combined
FIPS_runner('health_input',2,2024)

#### manual step: check csv files to make sure the format meets expectations and move files to a prep folder once they have been checked 
### data pre-processing checks - make sure columns in each file match only keeping columns that persist across the entire dataset 

column_name_check('prep/cost_p_income')
#clean up files that do not  by removing columns that are non consistant across files (found by running the check function first then manually creating the column to keep file)
column_clean_up('prep/education','EducationAttainment2021_cleaned.csv')
column_clean_up('prep/education','EducationAttainment2022_cleaned.csv')
column_clean_up('prep/education','EducationAttainment2023_cleaned.csv')
column_clean_up('prep/education','EducationAttainment2024_cleaned.csv')
column_name_check('prep/education')
column_name_check('prep/electric')
column_name_check('prep/gas')
column_name_check('lprep/abor_force')
column_name_check('prep/median_monthly')
column_name_check('prep/occupaction_production')
column_name_check('prep/occupancy_status')
column_name_check('prep/occupation_management')
column_name_check('prep/occupation_nature')
column_name_check('prep/occupation_sales')
column_name_check('prep/occupation_service')
column_name_check('prep/occupation_total')
column_name_check('prep/poverty_median')
column_name_check('prep/rent')
column_name_check('prep/transportation')
#clean up files that do not  by removing columns that are non consistant across files  
column_clean_up('health_input','health_input_2020 County Health Rankings Wisconsin Data - v1_0_cleaned.csv')
column_clean_up('health_input','health_input_2021 County Health Rankings Wisconsin Data - v1_cleaned.csv')
column_clean_up('health_input','health_input_2022 County Health Rankings Wisconsin Data - v2_cleaned.csv')
column_clean_up('health_input','health_input_2023 County Health Rankings Wisconsin Data - v3_cleaned.csv')
column_clean_up('health_input','health_input_2024 County Health Rankings Wisconsin Data - v2_cleaned.csv')
column_name_check('health_input')

### Combine files of the same dataset into a single file 
#### manual step here - placed all files into a single folder 
folder_path = 'CleanData'
folder_path = Path(folder_path)
file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
file_names.sort()

combine_csv_files(file_names,'CostPercentIncome')
combine_csv_files(file_names,'Education')
combine_csv_files(file_names,'Transportation')
combine_csv_files(file_names,'MedianMonthlyCostDollars')
combine_csv_files(file_names,'MedianRentDollars')
combine_csv_files(file_names,'Electric')
combine_csv_files(file_names,'Gas')
combine_csv_files(file_names,'Occupancy')
combine_csv_files(file_names,'Management')
combine_csv_files(file_names,'Natural')
combine_csv_files(file_names,'Service')
combine_csv_files(file_names,'Sales')
combine_csv_files(file_names,'Total')
combine_csv_files(file_names,'Production')
combine_csv_files(file_names,'PovertyAndMedianIncome')
combine_csv_files(file_names,'PovertyAndMedianIncome')
saipe_unpivot('SnapBenafits_cntysnap_cleaned.csv','SNAP','SnapBenafits')
combine_csv_files(file_names,'LaborForce')
combine_csv_files(file_names,'Health')



### JOIN ALL files into single dataset 
#clean up each dataset file to prepare it for the final dataset 
county_df= final_staging_runner('CleanData/combined').sort_values(by="county")
#join all datasets into final dataset 
combine_staging_files('CleanData/final_staging') 
