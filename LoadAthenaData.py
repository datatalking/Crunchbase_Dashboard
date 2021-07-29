
import boto3

ath = boto3.client('athena') with open(sys.argv[1]) as ddl:
    ath.start_query_execution(
        QueryString=ddl.read(),
        ResultConfiguration={'OutputLocation': 's3://'+ sys.argv[2] + '/'});