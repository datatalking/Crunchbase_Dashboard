
import boto3

ath = boto3.client('athena')

ath.start_query_execution(
    QueryString='create database mangolassi',
    ResultConfiguration={'OutputLocation': 's3://mango-lassi-costings/queries/'})
