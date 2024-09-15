from google.cloud import bigquery
import pandas as pd
from sqlalchemy import create_engine
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from hooks.ingestion_api_hook import IngestionApiHook
from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook  # BigQuery Hook for handling BQ operations
from io import StringIO  # For in-memory file handling

# PostgreSQL connection settings
POSTGRES_USER = 'airflow'
POSTGRES_PASSWORD = 'airflow'
POSTGRES_HOST = 'postgres'
POSTGRES_PORT = '5432'
POSTGRES_DB = 'airflow'

# BigQuery settings
PROJECT_ID = 'pacific-ethos-433305-u0'  # Replace with your project ID
DATASET_ID = 'The_Weather_Data'  # Dataset name (not full ID)
TABLE_ID = 'The_Weather_Table'  # Table name (not full ID)

def call_api(api_key, end_date):
    hook = IngestionApiHook(http_conn_id='ingestion_api', method='GET')
    response = hook.run(endpoint=f'/v2.0/history/daily?lat=59.33&lon=18.07&key={api_key}&start_date=2024-02-09&end_date={end_date}')

    if isinstance(response, dict) and 'data' in response:
        data = response['data']

        # Convert list of dictionaries to a DataFrame
        df = pd.json_normalize(data)

        # Clean the DataFrame
        df = df[['clouds', 'max_temp_ts', 'max_wind_spd', 'min_temp', 'revision_status', 'snow', 'solar_rad', 'temp', 'wind_gust_spd', 'wind_spd']]

        # Rename columns if needed (for example purposes, these match your desired format)
        df.columns = ['clouds', 'max_temp_ts', 'max_wind_spd', 'min_temp', 'revision_status', 'snow', 'solar_rad', 'temp', 'wind_gust_spd', 'wind_spd']

        # Create SQLAlchemy engine for PostgreSQL
        engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')

        # Save DataFrame to PostgreSQL, replacing old data
        table_name = 'weather_data'  # Choose your table name
        df.to_sql(table_name, engine, if_exists='replace', index=False)  # 'replace' will drop the table and recreate it

        print('DataFrame saved to PostgreSQL successfully.')

        # Upload DataFrame to BigQuery
        upload_to_bigquery(df)

    else:
        print("Unexpected response format or missing 'data' key")

def upload_to_bigquery(df):
    # Define BigQuery table in the correct format: project_id.dataset_id.table_id
    table_id = f'{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}'
    
    # Create BigQuery hook to use connection google_cloud_default
    hook = BigQueryHook(gcp_conn_id='google_cloud_default', use_legacy_sql=False)
    client = hook.get_client()  # Get BigQuery client

    # Upload DataFrame to BigQuery
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")  # Replace table data
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

    # Wait for the job to complete
    job.result()

    print(f'DataFrame uploaded to BigQuery table: {table_id}')

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 9, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=3)
}

with DAG(
    'example_python_operator_hook',
    default_args=default_args,
    schedule_interval='@daily'
) as dag:

    api_call_task = PythonOperator(
        task_id='call_api_task',
        python_callable=call_api,
        op_kwargs={
            'api_key': '08bf7a66cf314645a58149cc18b37957',
            'end_date': datetime.now().strftime('%Y-%m-%d')  
        }
    )
