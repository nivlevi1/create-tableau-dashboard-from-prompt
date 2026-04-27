from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id="daily_rates_ingestion",
    description="Fetch USD/ILS daily rate and update CSV (Mon-Fri at 20:00 UTC)",
    schedule_interval="0 20 * * 1-5",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["forex", "ils"],
) as dag:

    ingest = BashOperator(
        task_id="run_ingestion",
        bash_command="docker exec python_runner python /app/daily_rates_ingestion.py",
    )
