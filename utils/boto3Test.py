import boto3
from botocore.config import Config

my_config = Config(
    region_name = 'us-east-1',
    signature_version = 'v4',
)
ddb = boto3.client('dynamodb', config=my_config)
ddb.describe_limits()
