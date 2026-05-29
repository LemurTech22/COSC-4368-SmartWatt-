from src.data_ingestion.extractor import File_Extraction
from src.data_ingestion.schema import energy_schema
def main():
    print("[1/5] Fetching data... \nPlease Wait... ")
    with File_Extraction() as extractor:
        energy_data = extractor.csv_file_path()
        weather_data = extractor.fetch_weather(2022, 10, 4, 2024, 11, 4)
    print("[1/5] Data Collected!")


    print("[2/5] Verifying schema:")
    try:
        energy_schema.validate(energy_data, lazy=True)
        print("[2/5] Schema Validated!")
    except Exception as e:
        print(f"Schema Validation Failed: {e}")

    print("[3/5] Loading Data into GCS \n Please Wait...")
    #TODO add logic for loading data into gcs. remember to keep them seperate.
    #once complete we work in big query
if __name__== "__main__":
    main()