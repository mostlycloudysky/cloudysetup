from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from .cloudcontrol_client import create_resource, get_resource_request_status
from .utils import extract_aws_credentials
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware


app = FastAPI()

# Initialize the limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(SlowAPIMiddleware)


class MessageRequest(BaseModel):
    message: str


class ResourceRequestStatus(BaseModel):
    request_token: str


class MessageResponse(BaseModel):
    status: str
    details: dict


@app.get("/")
@limiter.limit("3/minute")
def read_root(request: Request):
    return {"message:": "Hello World"}


@app.post("/message")
@limiter.limit("3/minute")
def get_message(msgrequest: MessageRequest, request: Request):
    if not msgrequest.message:
        raise HTTPException(status_code=400, detail="Message is empty")

    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(request)

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
