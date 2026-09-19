import boto3

def cloudwatch(): return boto3.client('cloudwatch')
def autoscaling(): return boto3.client('autoscaling')
def lambda_client(): return boto3.client('lambda')
