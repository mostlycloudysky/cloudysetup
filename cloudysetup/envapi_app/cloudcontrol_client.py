import boto3
import json
import os
import re


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


def delete_resource(
    type_name: str,
    identifier: str,
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

    response = cloudcontrol_client.delete_resource(
        TypeName=type_name, Identifier=identifier
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

    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 1,
        "top_p": 0.999,
        "top_k": 250,
        "stop_sequences": [],
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(native_request)

    MODEL_ID = "anthropic.claude-v2"
    response = bedrock.invoke_model(
        body=request,
        modelId=MODEL_ID,
    )

    model_response = json.loads(response["body"].read())
    response_text = model_response["content"][0]["text"]
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if json_match:
        response_json = json.loads(json_match.group())
        print(response_json)
        return response_json
    else:
        raise ValueError("No valid JSON found in the model response")


def ai_suggestions(prompt: str):

    if "ECS_CONTAINER_METADATA_URI" in os.environ:
        bedrock = boto3.client(service_name="bedrock-runtime")
    else:
        session = boto3.Session()
        bedrock = session.client(service_name="bedrock-runtime")

    native_request = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 300,
        "temperature": 1,
        "top_p": 0.999,
        "top_k": 250,
        "stop_sequences": [],
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}],
            }
        ],
    }

    request = json.dumps(native_request)

    MODEL_ID = "anthropic.claude-v2"
    response = bedrock.invoke_model(
        body=request,
        modelId=MODEL_ID,
    )

    model_response = json.loads(response["body"].read())
    response_text = model_response["content"][0]["text"]
    json_match = re.search(r"\[.*?\]", response_text, re.DOTALL)
    if json_match:
        response_json = json.loads(json_match.group())
        print(response_json)
        return response_json
    else:
        raise ValueError("No valid JSON found in the model response")
