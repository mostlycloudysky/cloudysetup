import boto3
import json

cloudcontrol_client = boto3.client("cloudcontrol", region_name="us-east-1")


def create_resource(type_name: str, desired_state: str):
    response = cloudcontrol_client.create_resource(
        TypeName=type_name, DesiredState=json.dumps(desired_state)
    )

    return response


def get_resource_request_status(request_token: str):
    response = cloudcontrol_client.get_resource_request_status(
        RequestToken=request_token
    )
    return response
