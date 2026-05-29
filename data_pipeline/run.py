from src.data_ingestion.extractor import File_Extraction

def main():
    print("[1/5] Fetching data... \nPlease Wait... ")
    with File_Extraction() as extractor:
        energy_data = extractor.csv_file_path()
        weather_data = extractor.fetch_weather(2022, 10, 4, 2024, 11, 4)
    print("[1/5] Data Collected!")

    print("[2/5] Loading Data into GCS \n Please Wait...")
    #TODO add logic for loading data into gcs. remember to keep them seperate.
    #once complete we work in big query
if __name__== "__main__":
    main()