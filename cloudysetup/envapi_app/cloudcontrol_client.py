import boto3
import json


def create_resource(
    type_name: str,
    desired_state: str,
    aws_access_key: str,
    aws_secret_key: str,
    aws_session_token: str = None,
):

    if aws_session_token:
        cloudcontrol_client = boto3.client(
            "cloudcontrol",
            region_name="us-east-1",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
        )
    else:
        cloudcontrol_client = boto3.client(
            "cloudcontrol",
            region_name="us-east-1",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )

    response = cloudcontrol_client.create_resource(
        TypeName=type_name, DesiredState=json.dumps(desired_state)
    )

    return response


def get_resource_request_status(
    request_token: str, aws_access_key: str, aws_secret_key: str, aws_session_token: str
):
    if aws_session_token:
        cloudcontrol_client = boto3.client(
            "cloudcontrol",
            region_name="us-east-1",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            aws_session_token=aws_session_token,
        )
    else:
        cloudcontrol_client = boto3.client(
            "cloudcontrol",
            region_name="us-east-1",
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
        )
    response = cloudcontrol_client.get_resource_request_status(
        RequestToken=request_token
    )
    return response
