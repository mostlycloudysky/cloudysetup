from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from .cloudcontrol_client import create_resource, get_resource_request_status
from .utils import extract_aws_credentials

app = FastAPI()


class MessageRequest(BaseModel):
    message: str


class ResourceRequestStatus(BaseModel):
    request_token: str


class MessageResponse(BaseModel):
    status: str
    details: dict


@app.get("/")
def read_root():
    return {"message:": "Hello World"}


@app.post("/message")
def get_message(request: MessageRequest, req: Request):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is empty")

    print("Hello, I am here")

    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(req)

    print("Hello, I am here")
    print(aws_access_key, aws_secret_key, aws_session_token)

    resource_type = "AWS::EC2::Instance"
    configuration = {"InstanceType": "t2.micro", "ImageId": "ami-08a0d1e16fc3f61ea"}

    try:
        response = create_resource(
            resource_type,
            configuration,
            aws_access_key,
            aws_secret_key,
            aws_session_token,
        )
        return {"status": "success", "details": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/resource-status")
def get_resource_status(request: ResourceRequestStatus, req: Request):
    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(req)
    try:
        response = get_resource_request_status(
            request.request_token, aws_access_key, aws_secret_key, aws_session_token
        )
        return {"status": "success", "details": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/")
def read_root():
    return {"message:": "Hello World"}
