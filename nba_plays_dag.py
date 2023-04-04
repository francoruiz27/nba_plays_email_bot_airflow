from __future__ import annotations
import pendulum
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from nba_proyect.main import get_plays, add_plays_by_player, check_if_quarter_ended, get_today_game_info, Player
import time


def _check_for_plays():                 #I could pass the game through conf, then I'll find out how
    game = get_today_game_info('pacers')
    if game.id == 0:
        print('No games today')
    else:
        player = Player('Nembhard', [])
        while game.actual_quarter < 5:
            print(game.actual_quarter)
            plays = get_plays(game)
            player = add_plays_by_player(plays, player)
            game = check_if_quarter_ended(plays, game)
            time.sleep(10)
    print('Game finished!')

with DAG(
    dag_id="nba_plays_dag3",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=None,
    tags=["example"],
) as dag:
    
    today_game = PythonOperator(task_id='today_game', python_callable = _check_for_plays)

    today_game