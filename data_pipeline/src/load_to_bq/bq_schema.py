#run me once only 
from google.cloud import bigquery,storage
from google.api_core.exceptions import Conflict
#this code is one time use, and sets up cleaned up tables for dbt to store and use.
def main():
    client=bigquery.Client()
    job_config=bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("","STRING")
        ],
    )