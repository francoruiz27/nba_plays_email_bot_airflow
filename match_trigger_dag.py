from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from pendulum import datetime, duration
from nba_proyect.main import get_today_game_info
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python_operator import PythonOperator


default_args = {
    "owner": "Franco",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": duration(minutes=5),
}


def _branch_game_today():
    game_info = get_today_game_info('pacers')
    if game_info.id == 0:
        return 'no_games_today'
    else:
        return "trigger_dag"
    
def _no_games_today():
    print('There are no games today')

with DAG(
    dag_id="trigger_nba",
    start_date=datetime(2021, 1, 1, tz="UTC"),
    catchup=False,
    schedule="0 2 * * *",
    tags=["trigger", "nba"],
) as dag:
    
    branch_func = BranchPythonOperator(
        task_id='is_there_a_match_today', 
        python_callable = _branch_game_today
    )
    
    trigger_dependent_dag = TriggerDagRunOperator(
        task_id="trigger_dag",
        trigger_dag_id="nba_plays_dag3",
        wait_for_completion=False,
        #conf={"game_info": get_today_game_info('spurs')},
        execution_date=get_today_game_info('pacers').date_time,
        reset_dag_run=True,
    )

    no_games_today = PythonOperator(
        task_id='no_games_today', 
        python_callable = _no_games_today
    )

    branch_func >> [trigger_dependent_dag, no_games_today]
