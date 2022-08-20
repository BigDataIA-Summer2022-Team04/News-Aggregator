import os
from datetime import datetime
from pathlib import Path
from datetime import datetime, timedelta
from airflow import DAG
import pymongo
import json
import pandas as pd
from google.cloud import storage
import shutil
import glob
import time
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from great_expectations_provider.operators.great_expectations import GreatExpectationsOperator
from great_expectations.core.batch import BatchRequest
from great_expectations.data_context.types.base import (
    DataContextConfig,
    CheckpointConfig
)


base_path = "/opt/airflow/working_data"
data_dir = os.path.join(base_path, "News-Aggregator", "great_expectations", "data")
ge_root_dir = os.path.join(base_path, "News-Aggregator", "great_expectations")
report_dir = os.path.join(ge_root_dir, "uncommitted/data_docs/local_site/validations/nyt_raw_data_suite" )

def extract_data_from_mongodb():
    mongo_client = pymongo.MongoClient("mongodb+srv://airflow_schema:################@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = mongo_client["news"]
    mycollection = mydb["daily_reporting"]
    query_output = list(mycollection.find({}))
    df = pd.io.json.json_normalize(query_output)
    df.to_csv(os.path.join(data_dir, "output.csv"), index=False)
    return os.path.join(data_dir, "output.csv")

def clear_mongodb():
    mongo_client = pymongo.MongoClient("mongodb+srv://airflow_schema:################@news.xiubnpm.mongodb.net/?retryWrites=true&w=majority")
    mydb = mongo_client["news"]
    mycollection = mydb["daily_reporting"]
    mycollection.delete_many({})
    return 

def upload_blob():
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"
    time.sleep(10)

    ok = glob.glob('/opt/airflow/working_data/News-Aggregator/great_expectations/uncommitted/data_docs/local_site/validations/nyt_raw_data_suite/*/*/*.*')
    # /airflow_docker/working_data/News-Aggregator/great_expectations/uncommitted/data_docs/local_site/validations/nyt_raw_data_suite

    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/opt/airflow/keys/key.json"
    bucket_name="news-great-expectations-report"
    source_file_name=ok[0]
    destination_blob_name= ok[0].split("/")[-2] + ".html"
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

    shutil.rmtree("/opt/airflow/working_data/News-Aggregator/great_expectations/uncommitted/data_docs/local_site/validations/nyt_raw_data_suite")
    return f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"



with DAG(
        dag_id="great_expectations_report_v2",
        start_date = days_ago(0),
        catchup=False,
        schedule_interval="0 6 * * *"
) as dag:

    clean_dir = BashOperator(
        task_id="clean_dir",
        bash_command='echo "Cleaning following files" ; ls -l /opt/airflow/working_data/News-Aggregator/great_expectations/data ; rm -rf /opt/airflow/working_data/News-Aggregator/great_expectations/data/*',
    )

    extract_data_from_mongodb = PythonOperator(
        task_id='extract_data_from_mongodb',
        python_callable = extract_data_from_mongodb,
        provide_context=True,
        dag=dag,
    )

    ge_data_context_root_dir_with_checkpoint_name_pass = GreatExpectationsOperator(
        task_id="ge_data_context_root_dir_with_checkpoint_name_pass",
        data_context_root_dir=ge_root_dir,
        checkpoint_name="nyt_raw_data_suite_checkpoint_v1.1",
        fail_task_on_validation_failure=False
    )

    upload_blob = PythonOperator(
        task_id='upload_blob',
        python_callable = upload_blob,
        provide_context=True,
        dag=dag,
    )

    clear_mongodb = PythonOperator(
        task_id='clear_mongodb',
        python_callable = clear_mongodb,
        provide_context=True,
        dag=dag,
    )


(
    clean_dir >> extract_data_from_mongodb >> ge_data_context_root_dir_with_checkpoint_name_pass >> upload_blob >> clear_mongodb

)