from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from .cloudcontrol_client import (
    create_resource,
    delete_resource,
    update_resource,
    get_resource_request_status,
    invoke_bedrock_model,
    ai_suggestions,
)
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
    TypeName: str
    Properties: dict


class ResourceRequestStatus(BaseModel):
    request_token: str


class MessageResponse(BaseModel):
    status: str
    details: dict


class TemplateRequest(BaseModel):
    prompt: str
    properties: dict = {}


class TemplateResponse(BaseModel):
    request_data: dict
    suggestions: list = []


class ResourceRequest(BaseModel):
    TypeName: str
    Properties: dict


class DeleteResourceRequest(BaseModel):
    TypeName: str
    Identifier: str


class UpdateResourceRequest(BaseModel):
    TypeName: str
    Identifier: str
    PatchDocument: str


@app.get("/")
@limiter.limit("3/minute")
def read_root(request: Request):
    return {"message:": "Hello World"}


@app.post("/generate-template", response_model=TemplateResponse)
async def generate_template(template: TemplateRequest, request: Request):

    try:
        # Invoke bedrock model
        bedrock_response = invoke_bedrock_model(template.prompt)

        # Invoke suggestions model to provide suggestions
        suggestions_response = ai_suggestions(
            f"Create a suggested changes for each objects such as unique name and more descriptive etc. without suggesting values  and expand  for this AWS cloud control API request body and generate the suggestions in a array of strings. {bedrock_response}"
        )
        print("Suggested response:", suggestions_response)
        suggestions = [
            "Change the TopicName to a unique value",
            "Set DisplayName to something more descriptive",
        ]
        return {"request_data": bedrock_response, "suggestions": suggestions_response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/create-resource")
@limiter.limit("3/minute")
def create_resource_endpoint(resource_request: ResourceRequest, request: Request):
    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(request)

    resource_type = resource_request.TypeName
    configuration = resource_request.Properties

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


@app.post("/delete-resource")
@limiter.limit("3/minute")
def delete_resource_endpoint(resource_request: DeleteResourceRequest, request: Request):
    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(request)

    resource_type = resource_request.TypeName
    identifier = resource_request.Identifier

    try:
        response = delete_resource(
            resource_type,
            identifier,
            aws_access_key,
            aws_secret_key,
            aws_session_token,
        )
        return {"status": "success", "details": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/update-resource")
@limiter.limit("3/minute")
def update_resource_endpoint(resource_request: UpdateResourceRequest, request: Request):
    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(request)

    resource_type = resource_request.TypeName
    patch_document = resource_request.PatchDocument
    identifier = resource_request.Identifier

    try:
        response = update_resource(
            resource_type,
            identifier,
            patch_document,
            aws_access_key,
            aws_secret_key,
            aws_session_token,
        )
        return {"status": "success", "details": response}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/message")
@limiter.limit("3/minute")
def get_message(msgrequest: MessageRequest, request: Request):
    if not msgrequest.TypeName or not msgrequest.Properties:
        raise HTTPException(status_code=400, detail="Request is invalid..")

    aws_access_key, aws_secret_key, aws_session_token = extract_aws_credentials(request)

    resource_type = msgrequest.TypeName
    configuration = msgrequest.Properties

    print(f"Resource Type: {resource_type}")
    print(f"Configuration: {configuration}")

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
