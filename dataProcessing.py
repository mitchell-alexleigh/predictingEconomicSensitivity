# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#imports 
import pandas as pd 
from pathlib import Path
import shutil
### data prep functions 

# prep files with multi level hierarchies 
def hierarchy_Cleaner_level(p_folder,p_fileName,level,measure,year):
    filePath = f"{p_folder}/{p_fileName}"
    df = pd.read_csv(filePath)
    #add year column 
    df["Year"] = year
    ### FORMAT HIERARCHY FOR VALUES TO KEEP 
    # Create County Column 
    df["County"] = df["Label (Grouping)"]
    # Create level Column 
    df[level] = df["Label (Grouping)"]
    # Create Metric Column 
    df["Metric"] = df["Label (Grouping)"]

    #replace values of attribtues to keep 
    df.loc[~df["County"].str.contains("County", na=False), "County"] = pd.NA
    df.loc[~df[level].str.contains(level, na=False), level] = pd.NA

    #fill values to keep
    df['County'] = df['County'].ffill()
    df[level] = df[level].ffill(limit=1)

    #Filter DF 
    df = df[df[level].notna()]
    df = df[df['Metric'].str.contains(measure, case=False)]

    #Drop hierarchy columns 
    df.drop(columns=['Label (Grouping)', level, 'Metric'],inplace=True)

    #export 
    fileName = p_fileName.split('.')[0]
    csv_name = f"{fileName}_{level}_cleaned.csv"
    df.to_csv(csv_name, index=False)

# runs cleaner funtion for each file in a dataset folder 
def ucdc_level_runner(p_folder,level,measure): 
    folder_path = Path(p_folder)
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
    files = file_names[0:]
    files.sort(reverse=True)
    year = 2024 
    for file in files:
        hierarchy_Cleaner_level(folder_path,file,level,measure,year)
        year = year-1 

#prep files with single level hierarchies 
def hierarchy_Cleaner(p_folder,p_fileName,measure,year):
    filePath = f"{p_folder}/{p_fileName}"
    df = pd.read_csv(filePath)
    #add year column 
    df["Year"] = year
    ### FORMAT HIERARCHY FOR VALUES TO KEEP 
    # Create County Column 
    df["County"] = df["Label (Grouping)"]
    # Create Metric Column 
    df["Metric"] = df["Label (Grouping)"]

    #replace values of attribtues to keep 
    df.loc[~df["County"].str.contains("County", na=False), "County"] = pd.NA

    #fill values to keep
    df['County'] = df['County'].ffill()

    #Filter DF 
    df = df[df['Metric'].str.contains(measure, case=False)]


    #Drop hierarchy columns 
    df.drop(columns=['Label (Grouping)','Metric'],inplace=True)

    #export 
    fileName = p_fileName.split('.')[0]
    csv_name = f"{fileName}_cleaned.csv"
    df.to_csv(csv_name, index=False)

# runs cleaner funtion for each file in a dataset folder     
def ucdc_runner(p_folder,measure): 
    folder_path = Path(p_folder)
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
    files = file_names[0:]
    files.sort(reverse=True)
    year = 2024 
    for file in files:
        hierarchy_Cleaner(folder_path,file,measure,year)
        year = year-1 
        

def excel_loader(p_folder,p_fileName,header_row):
    filePath = f"{p_folder}/{p_fileName}"
    header_row = header_row - 1 
    df = pd.read_excel(filePath, header=header_row)
    return df 


def FIPS_cleaner(p_folder,p_fileName,header_row,year): 
    df = excel_loader(p_folder,p_fileName,header_row)
    df.columns = df.columns.str.lower()
    try: 
        df = df[df["state fips code"] == 55]
    except: 
        pass
    try:
        df = df[df["state"].isin(["WI", "Wisconsin"])]
    except:
        pass
    #add year column 
    if year is not False:
        df["Year"] = year
    
    #export 
    fileName = p_fileName.split('.')[0]
    csv_name = f"{p_folder}_{fileName}_cleaned.csv"
    df.to_csv(csv_name, index=False)

# runs cleaner funtion for each file in a dataset folder 
def FIPS_runner(p_folder,header_row,start_year): 
    folder_path = Path(p_folder)
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.suffix.lower() in (".xls", ".xlsx")]
    files = file_names[0:]
    files.sort(reverse=True)
    year = start_year 
    for file in files:
        FIPS_cleaner(folder_path,file,header_row,year)
        if year is not False:
            year = year - 1

#function to unpivot file with years along the x axis 
def saipe_unpivot(file,metric_name,output_name): 
    df = pd.read_csv(f"CleanData/{file}")
    #drop year column that was added in previous step
    df = df.drop(columns="Year")
    #columns to maintain
    id_cols = ["state fips code", "county fips code", "name"]
    df = df.melt(id_vars=id_cols,var_name="date", value_name=metric_name)
    #clean up year column 
    df["Year"] = df["date"].str.extract(r"(\d{4})").astype(int)
    #drop column with month name 
    df = df.drop(columns="date")
    df.to_csv(f"CleanData/combined/{output_name}_combined.csv", index=False) 
    #move orginal file 
    shutil.move(f"CleanData/{file}", f"CleanData/archive/{file}") 
    
    return df 


### data pre-profiling functions (checks before multiple files of a single dataset before they are combined)
#get list of filenames 
def column_name_check(p_folder): 
    folder_path = Path(f'prep/{p_folder}')
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
    files = file_names[0:]
    files.sort(reverse=True)
    
    #ignore column names to keep file, old error file, or old column name file 
    ignore = ['column_names_to_keep.csv','errors.csv','column_names.csv']
    files = [x for x in files if x not in ignore]
    
    # Create a list of column names for each file
    column_names = {}
    
    for file in files:
        file_path = folder_path / file
        df = pd.read_csv(file_path, nrows=0)
        column_names[file] = df.columns.tolist()
        
    
    # Create a DataFrame of column names for each file
    df_columns = pd.DataFrame({
        file: pd.Series(columns)
        for file, columns in column_names.items()
        })
    #check if rows match, and drop records that match (hopefully all records are dropped)
    
    #AI USE the following 2 lines are AI generated based on the following prompt: modify my code. df_columns = df_columns.T.drop_duplicates().T is not behaving as expected. I want to drop the entire row if the entire row matches.
    df_columns = df_columns.loc[
        ~df_columns.apply(lambda row: row.nunique() == 1, axis=1)
    ]
    
    #print success message or export errors 
    if df_columns.empty:
        print(f"{p_folder} Files match.")
    else:
        df_columns.to_csv(folder_path / "errors.csv", index=False)
        print(f"{p_folder} Differences found. Exported to errors.csv.")
    # Export column names for last file
    df_last_file = pd.DataFrame({'Column Names': column_names[files[-1]]})
    df_last_file.to_csv(folder_path / "column_names.csv", index=False)
    
    return df_last_file

#use csv file with column names to keep to clean up column names 
def column_clean_up(p_folder,p_fileName): 
    keep_fileName = 'column_names_to_keep.csv'
    filePathKeep = f"{p_folder}/{keep_fileName}"
    df_keep = pd.read_csv(filePathKeep)
    filePath = f"{p_folder}/{p_fileName}"
    df_clean = pd.read_csv(filePath)
    
    # Keep only columns listed in df_keep following two lines where AI generated PROMT: help me finish my python script. So far I ingest a csv of column names I want to keep in a file export, then i ingest a second CSV, drop all columns in the second CSV where the column name is not in the df of column names to keep
    columns_to_keep = df_keep['Column Names'].tolist()
    df_clean = df_clean.loc[:, df_clean.columns.isin(columns_to_keep)]
    
    # Export cleaned CSV
    df_clean.to_csv(f"{p_folder}/{p_fileName}", index=False)

#combine files of the same dataset using a key term to identify files of the same dataset and name the outfile 
def combine_csv_files(file_names, search_term):
    matching_files = [x for x in file_names if search_term in x]
    df = pd.concat([pd.read_csv(f"CleanData/{file}") for file in matching_files], ignore_index=True)
    output_name = search_term
    df.to_csv(f"CleanData/combined/{output_name}_combined.csv", index=False) 
    for file in matching_files:
        shutil.move(f"CleanData/{file}", f"CleanData/archive/{file}") 
    return df

### final prep 
def final_staging (p_folder,p_fileName): 
    filePath = f"{p_folder}/{p_fileName}"
    df = pd.read_csv(filePath)
    #drop extra columns that contain the work 'code' (postal codes, fips codes...) 
    df = df.loc[:, ~df.columns.str.contains("code", na=False)]
    df = df.loc[:, ~df.columns.str.contains("state", na=False)]
    # make all columns lower case
    df.columns = df.columns.str.lower()
    
    #AI GENERATED - following 8 lines gernated with promt: Add a conditional statement after converting the column names to lowercase. If the filename contains "occupation", prepend the filename (without .csv) to every column name except year and county
    # If filename contains "occupation", prepend filename to column names
    if "occupation" in p_fileName.lower():
        file_prefix = Path(p_fileName).stem.lower()
        df.columns = [
            col if col in ["year", "county"]
            else f"{file_prefix}_{col}"
            for col in df.columns
        ]
        
    # make county values all uppercase 
    df["county"] = df["county"].str.upper()
    # trim leading and lagginf spaces before additional clean up 
    df["county"] = df["county"].str.strip()
    # remove word "county" from county column and get list of distinct county names  
    df["county"] = df["county"].str.replace("COUNTY", "", regex=False)
    df["county"] = df["county"].str.replace(",", "", regex=False)
    df["county"] = df["county"].str.replace("WISCONSIN", "", regex=False)
    df["county"] = df["county"].str.replace(" WI", "", regex=False)
    #clean up Saint Croix 
    df["county"] = df["county"].str.replace("ST.", "SAINT", regex=False)
    # trim leading and lagginf spaces after clean up 
    df["county"] = df["county"].str.strip()
    #convert year to int 
    df["year"] = df["year"].astype(int)
    # Filter year 2021 or greater and 2024 or less 
    #filtering year hear instead of at the orginal files incase I want to add more years later 
    df = df[df["year"] >= 2021]
    df = df[df["year"] <= 2024]
    #remove empty county values 
    df = df[df["county"].notna()]
    df = df[df["county"].notna() & (df["county"].str.strip() != "")]
    #output CSV 
    df.to_csv(f'CleanData/final_staging/{p_fileName}', index=False) 
    
    # Return distinct county names as a list
    return df["county"].unique().tolist()
    
def final_staging_runner(p_folder): 
    folder_path = Path(p_folder)
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
    file_names.sort()
    #initiate dict to store key, value pairs of county name and first file that county name appears in to track any oddities in county name 
    county_records = {}
    for file in file_names:
        try:
            #exports the clearned up dataset into the final staging folder for each file in the combined folder and keeps track of county names 
            counties = final_staging(folder_path, file)
            for county in counties:
                #add new unique counties to a full record of counties accross all files to check if all counties are valid of if any need to be manually updated 
                if county not in county_records:
                    #store key value pair in dict to keep track of which file contains an odd county name if one exists 
                    county_records[county] = file
        except Exception as e:
            print(f"Error processing {file}: {e}")
    # Create output DataFrame
    df_counties = pd.DataFrame(
        county_records.items(),
        columns=["county", "file_name"]
    )
    return df_counties 



def combine_staging_files(p_folder):
    folder_path = Path(p_folder)
    file_names = [f.name for f in folder_path.iterdir() if f.is_file() and f.name.endswith(".csv")]
    file_names.sort()

    # Load first CSV into dataframe
    df = pd.read_csv(folder_path / file_names[0])

    for file in file_names[1:]:
        try:
            # Load next CSV into dataframe
            filePath = f"{p_folder}/{file}"
            df_next = pd.read_csv(filePath)

            # Join dataframes on year and county
            df = df.merge(df_next,on=["year", "county"],how="outer")

        except Exception as e:
            print(f"Error processing {file}: {e}")

    #AI GERNATION: following 5 lines are AI generated with the following promt - modify df so year and county are first two column names
    # Move year and county to the first two columns
    df = df[["year", "county"] + [
        col for col in df.columns
        if col not in ["year", "county"]
    ]]

    # Output combined CSV
    df.to_csv("CleanData/final_dataset.csv", index=False)

    return df

