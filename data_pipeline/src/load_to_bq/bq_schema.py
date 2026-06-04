#run me once only 
from google.cloud import bigquery,storage
from google.api_core.exceptions import Conflict
#this code is one time use, and sets up cleaned up tables for dbt to store and use.
def main():
    client=bigquery.Client()
    forecast_meter_usage=[
        bigquery.SchemaField("ESIID","STRING", mode="REQUIRED"),
        bigquery.SchemaField("USAGE_START_TIME", "TIMESTAMP",mode="REQUIRED"),
        bigquery.SchemaField("USAGE_END_TIME", "TIMESTAMP", mode="REQUIRED")
    ]
    