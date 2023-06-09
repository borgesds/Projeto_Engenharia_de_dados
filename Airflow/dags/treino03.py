from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
import pandas as pd
import random


# Argumentos defaults
default_args = {
    'owner': 'Borges',
    'depends_on_past': False,
    'start_date': datetime(2023, 6, 24, 20, 1),
    'email': ['borges@gmail.com', 'borgesan@gmail.com'],
    'email_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1)
}

# Definirt a DEG
dag = DAG(
    'treino-eng_dados_03',
    description='Dados do Titanic e calcular a idade media Homens/Mulheres',
    default_args=default_args,
    schedule_interval='*/2 * * * *',
    max_active_runs=1,
)

get_data = DummyOperator(
    task_id='get_data',
    dag=dag
)

"""get_data = BashOperator(
    task_id='get-data',
    bash_command='curl https://raw.githubusercontent.com/A3Data/hermione/master/hermione/file_text/train.csv -o ~/Downloads/train.csv',
    dag=dag
)"""


def sorteia_h_m():
    return random.choice(['male', 'female'])


escolhe_h_m = PythonOperator(
    task_id='escolhe-h-m',
    python_callable=sorteia_h_m,
    dag=dag
)


def MouF(**context):
    value = context['task_instance'].xcom_pull(task_ids='escolhe-h-m')
    if value == 'male':
        return 'branch_homem'
    if value == 'female':
        return 'branch_mulher'


male_famale = BranchPythonOperator(
    task_id='condicional',
    python_callable=MouF,
    provide_context=True,
    dag=dag
)


def mean_homem():
    df = pd.read_csv('~/Downloads/train.csv')
    df = df.loc[df.Sex == 'male']
    print(f'Media de idade dos homens no Titanic: {df.Age.mean()}')


branch_homem = PythonOperator(
    task_id='branch_homem',
    python_callable=mean_homem,
    dag=dag
)


def mean_mulher():
    df = pd.read_csv('~/Downloads/train.csv')
    df = df.loc[df.Sex == 'female']
    print(f'Media de idade das mulheres no Titanic: {df.Age.mean()}')


branch_mulher = PythonOperator(
    task_id='branch_mulher',
    python_callable=mean_mulher,
    dag=dag
)

task_final = DummyOperator(
    task_id="task_final_ok",
    dag=dag
)


get_data >> escolhe_h_m >> male_famale >> [branch_homem, branch_mulher] >> task_final
