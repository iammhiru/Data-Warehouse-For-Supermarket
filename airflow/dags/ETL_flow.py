from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='ingest_csv_to_hive',
    default_args=default_args,
    description='Daily ingestion of CSV files into Hive staging tables via Spark using BashOperator',
    schedule_interval='@daily',
    start_date=datetime(2025, 6, 16),
    catchup=False,
    tags=['spark', 'hive', 'etl'],
) as dag:

    spark_ingest = BashOperator(
        task_id='spark_ingest',
        do_xcom_push=False,
        bash_command=(
            "set -o pipefail && "
            "spark-submit "
              "--master spark://spark-master:7077 "                      
              "--deploy-mode client "
              "/opt/airflow/code/stage.py "  
              "--process-date {{ ds }} "
            "2>&1"
        )
    )

    spark_ingest