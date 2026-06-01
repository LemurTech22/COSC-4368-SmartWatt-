from src.data_ingestion.extractor import File_Extraction
from src.data_ingestion.schema import energy_schema, weather_schema
from src.data_ingestion.uploader import file_uploader
from dotenv import load_dotenv
from google.cloud import storage
import os
def main():

    load_dotenv()
    bucket_name=os.getenv('BUCKET_NAME')
    storage_client=storage.Client()
    bucket=storage_client.bucket(bucket_name)


    print("[1/5] Fetching data... \nPlease Wait... ")
    with File_Extraction() as extractor:
        #notes for future need to get the time when scheduler runs...
        #dates in format yyyy, mm, dd
        start_year,start_month,start_day = 2022, 10, 4
        end_year,end_month,end_day = 2024, 11, 4 
        energy_data = extractor.csv_file_path()
        weather_data = extractor.fetch_weather(start_year, start_month, start_day, end_year, end_month, end_day)
    print("[1/5] Data Collected!")


    print("[2/5] Verifying schema:")
    try:
        energy_schema.validate(energy_data, lazy=True)
        weather_schema.validate(weather_data, lazy=True)

        print("[2/5] Raw Data Schemas Validated!")
    except Exception as e:
        print(f"Schema Validation Failed: {e}")

    print("[3/5] Loading Data into GCS \n Please Wait...")
    #once complete we work in big query
    with file_uploader(bucket) as uploader:
        path = uploader.upload_datasets(energy_data, weather_data)

    #working with Big Query
    
if __name__== "__main__":
    main()