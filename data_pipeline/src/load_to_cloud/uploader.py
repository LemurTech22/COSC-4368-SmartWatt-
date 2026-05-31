#used to upload data to GCS
#try to use 2 functions one to run and the other to set file pathing
from dotenv import load_dotenv
from google.cloud import storage
from datetime import datetime
import pandas as pd
import os
import io

#we must convert from csv or whatever format to parquet to save tons of space.
class file_uploader:
    def __init__(self):
        load_dotenv()
        self.bucket_name=os.getenv('BUCKET_NAME')
        
    def __enter__(self):
        self.storage_client=storage.Client()
        self.bucket=self.storage_client.bucket(self.bucket_name)
        return self
    
    def __exit__(self,exc_type, exc_val, exc_tb):
        self.storage_client.close()
        
    #pass weather folder and energy folder.
    def file_directory_creation(self,dataset_name: str)-> str:
        now=datetime.now()
        bucket_folder="raw"
        return(
            f"{bucket_folder}/"
            f"{dataset_name}/"
            #f"year-{now.year}/"
            f"month-{now.month:02d}/"
            f"day-{now.day:02d}/"
            f"{dataset_name}.parquet"
        )
    
    def upload_dataframe(self,df:pd.DataFrame,file_path: str):
        
        buffer=io.BytesIO()

        df.to_parquet(buffer, index=False,engine="pyarrow")

        blob=self.bucket.blob(file_path)
        blob.upload_from_string(
            buffer.getvalue(),
            content_type='application/octet-stream'
        )
        print(f"Uploaded to {file_path}")

    def upload_datasets(self,energy_df, weather_df):
        datasets={
            "energy": energy_df,
            "weather": weather_df
        }
        for dataset_name, df in datasets.items():
            file_path=self.file_directory_creation(dataset_name)

            self.upload_dataframe(
                df=df,
                file_path=file_path
            )
            blob = self.bucket.blob(file_path)
            df = pd.read_parquet(io.BytesIO(blob.download_as_bytes()))

            print(f"size of {dataset_name}: ",df.shape)
                
    #create file directories for the files
    #create var for file directory and names
    #    raw_energy_data
    #    raw_temperature_d
    # upload_to_GCS(file_to_upload, title, filepath)
    #    connect to GCS
    #   combine file directory set them in parquet. 
    #    upload to GCS
