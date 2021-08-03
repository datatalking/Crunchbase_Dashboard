import boto3

ddl_script_name = str(sys.argv[1])
arg_aws_access_key_id = str(sys.argv[2])
arg_aws_secret_access_key = str(sys.argv[3])
arg_region_name = str(sys.argv[4])
s3_bucket_name = str(sys.argv[5])

ath = boto3.client('athena', region_name=arg_region_name, aws_access_key_id=arg_aws_access_key_id,
    aws_secret_access_key=arg_aws_secret_access_key)

with open(ddl_script_name) as ddl:
    ath.start_query_execution(
        QueryString=ddl.read(),
        ResultConfiguration={'OutputLocation': 's3://'+ s3_bucket_name + '/'})