import boto3
import json
import os


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


def invoke_bedrock_model(prompt: str):

    if "ECS_CONTAINER_METADATA_URI" in os.environ:
        bedrock = boto3.client(service_name="bedrock-runtime")
    else:
        session = boto3.Session()
        bedrock = session.client(service_name="bedrock-runtime")

    prompt_body = json.dumps(
        {
            "prompt": prompt,
            "maxTokens": 512,
            "temperature": 0.7,
        }
    )

    MODEL_ID = "ai21.j2-ultra-v1"
    response = bedrock.invoke_model(
        body=prompt_body,
        modelId=MODEL_ID,
        accept="application/json",
        contentType="application/json",
    )

    model_response = json.loads(response["body"].read())
    response_text = model_response["completions"][0]["data"]["text"]
    return json.loads(response_text)
