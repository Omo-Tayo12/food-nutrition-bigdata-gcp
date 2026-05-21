import os
from google.cloud import bigquery

def load_parquet_to_bigquery():
    client = bigquery.Client()
    project_id = client.project
    
    table_id = f"{project_id}.nutrition.batch_nutrition_facts"
    uri = "gs://food-nutrition-processed/clean_nutrition_parquet/*"
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    
    print(f"Loading data from {uri} into {table_id}...")
    load_job = client.load_table_from_uri(uri, table_id, job_config=job_config)
    load_job.result()  # Wait for the load to finish
    print("Data loaded successfully into BigQuery!")

if __name__ == "__main__":
    load_parquet_to_bigquery()