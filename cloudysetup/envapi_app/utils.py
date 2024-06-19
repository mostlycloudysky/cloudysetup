from fastapi import HTTPException, Request


def extract_aws_credentials(req: Request):

    aws_access_key = req.headers.get("aws-access-key")
    aws_secret_key = req.headers.get("aws-secret-key")
    aws_session_token = req.headers.get("aws-session-token", None)

    if not aws_access_key or not aws_secret_key:
        raise HTTPException(status_code=400, detail="AWS credentials not provided")

    return aws_access_key, aws_secret_key, aws_session_token
