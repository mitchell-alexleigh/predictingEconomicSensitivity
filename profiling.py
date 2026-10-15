#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Oct 10 19:47:56 2026

@author: alex
"""
import pandas as pd 

filePath = "CleanData/final_dataset.csv"
df = pd.read_csv(filePath)

df_head = df.head()
df_shape = df.shape
df_cols = df.columns
df_describe = df.describe()
missing_val = df.isnull().sum().to_frame("missing_count")


# get columns with more than 75% missing data 
high_missing_val = missing_val[missing_val["missing_count"] <= 218]

#get number of null values for each county and year 
#get all count and years from df in new df 
null_count_df = df[["county", "year"]].copy()
# get count of nulls from final dataset df and add column of null counts to county and year df 
null_count_df["null_count"] = df.drop(columns=["county", "year"]).isnull().sum(axis=1)

print(df.info())