
from google.cloud import bigquery
import sys

table_map={
    "energy": "raw_meter_usage",
    "weather": "raw_weather"
}
def ingest(bucket: str, paths: dict, dataset: str="smartwatts"):
    client=bigquery.Client()
    dataset_bq= bigquery.Dataset(f"{client.project}.{dataset}")

    try:
        client.create_dataset(dataset_bq)
        print(f"Created dataset {client.project}.{dataset}")
    except Exception:
        print("Dataset already created\nContinuing...")

    for key, table in table_map.items():
        if key not in paths:
            print(f"Missing path for {key}")
            sys.exit(1)
        #gets link from our data source aka GCS.
        uri = f"gs://{bucket}/{paths[key]}"
        full_table= f"{client.project}.{dataset}.{table}"

        #loads file into big query
        #gets the link from gcs, and puts it into full table aka new location in big query.
        #so we are expecting a parquet file
        #write dis adds rows instead of overwriting
        #auto reads the columns and types from the file
        job=client.load_table_from_uri(
            uri,
            full_table,
            job_config=bigquery.LoadJobConfig(
                source_format=bigquery.SourceFormat.PARQUET,
                write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
                autodetect=True,
            ),
        )
        job.result()
        print(f"Loaded {client.get_table(full_table).num_rows:,} rows → {full_table}")
