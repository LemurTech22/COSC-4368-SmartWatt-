#run me once only 
from google.cloud import bigquery,storage
#Lets think should i pass the file paths from gcs to this file or create a function for it?


def main():
    client=bigquery.Client()
    job_config=bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("","STRING")
        ]
    )