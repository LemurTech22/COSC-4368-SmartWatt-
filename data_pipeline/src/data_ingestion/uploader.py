#used to upload data to GCS

from datetime import datetime
import pandas as pd
import io

#we must convert from csv or whatever format to parquet to save tons of space.
class file_uploader:
    def __init__(self,bucket):
        self.bucket=bucket
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type, exc_val, exc_tb):
        pass
        
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
    
    def upload_dataframe_to_GCS(self,df:pd.DataFrame,file_path: str):
        
        buffer=io.BytesIO()

        df.to_parquet(buffer, index=False,engine="pyarrow")

        blob=self.bucket.blob(file_path)
        blob.upload_from_string(
            buffer.getvalue(),
            content_type='application/octet-stream'
        )
        print(f"Uploaded to {file_path}")

    def upload_datasets(self,energy_df, weather_df):
        weather_df = weather_df.reset_index().rename(columns={"time": "timestamp"})
        datasets={
            "energy": energy_df,
            "weather": weather_df
        }
        paths={}
        for dataset_name, df in datasets.items():
            file_path=self.file_directory_creation(dataset_name)

            self.upload_dataframe_to_GCS(
                df=df,
                file_path=file_path
            )
            paths[dataset_name]=file_path

            blob = self.bucket.blob(file_path)
            df = pd.read_parquet(io.BytesIO(blob.download_as_bytes()))

            print(f"size of {dataset_name}: ",df.shape)
        return paths
                
    #create file directories for the files
    #create var for file directory and names
    #    raw_energy_data
    #    raw_temperature_d
    # upload_to_GCS(file_to_upload, title, filepath)
    #    connect to GCS
    #   combine file directory set them in parquet. 
    #    upload to GCS
