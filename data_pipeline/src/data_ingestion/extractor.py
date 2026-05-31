"""
This file is mainly for grabbing data and preparing it for upload to gcs.

Design Logic: 
    IF energy Data or API give no new data we end the pipeline and we prevent overwrites wasteful resources. 
    
    else
    
    Energy data goes until 2024
    so we must forecast our data past this date. 
    
    API also must grab the data at todays date

    For the data we dont overwrite the data we append the data or merge the data to prevent too much usage and duplication.

    Perform checks in gcs if directory and files exist in the cloud.

    for the overlap we can find schedule on todays time and date pull and subtracting it by our buffer window. aka 1-2hrs before api pull.
    Delete data older than 5 days.

    But start simple 
"""
import pandas as pd
#==================================
#Used for Meteostate api
#==================================
from datetime import datetime
from meteostat import Point, Hourly


class File_Extraction:
    def __init__(self):
        pass
    def __enter__(self):
        return self
    def __exit__(self,exc_type, exc_val, exc_tb):
        pass

    def csv_file_path(self):
        file_path = "data/Dataset.csv"

        print("Verifying Energy data is filled.")

        energy_df = pd.read_csv(file_path)
        print(energy_df.columns.to_list())
        print(energy_df.shape)
        print(energy_df.dtypes)
        print(energy_df.info)
        print({col: energy_df[col].unique() for col in energy_df.columns})

        return energy_df

    def fetch_weather(self, start_year, start_month, start_day, end_year, end_month, end_day):

       # Define the time period and location
        start = datetime(start_year, start_month, start_day) #changed dates need to revert back to original start and end time
        end = datetime(end_year, end_month, end_day)
        Houston = Point(29.7604, -95.3698, 13)

        # Fetch hourly weather data
        print("Grabbing data from MeteoStat.")
        weather_df = Hourly(Houston, start, end).fetch()
        
        if weather_df.empty:
            raise ValueError("API returned no data for the given time range. Data will be ignored")
        else:
            print("Verifying Temperature data is filled.")

            print(weather_df.columns.to_list())
            print(weather_df.shape)
            print(weather_df.dtypes)
            print(weather_df.info)
            print({col: weather_df[col].unique() for col in weather_df.columns})

            return weather_df
            