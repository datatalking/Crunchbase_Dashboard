
import boto3

ath = boto3.client('athena')with open('crunchbase_organizations.ddl') as ddl:
    ath.start_query_execution(
        QueryString=ddl.read(),
        ResultConfiguration={'OutputLocation': 's3://crunchbase_dashboard/'})