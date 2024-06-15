from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class MessageRequest(BaseModel):
    message: str


class MessageResponse(BaseModel):
    message: str


@app.get("/")
def read_root():
    return {"message:": "Hello World"}


@app.post("/message")
def get_message(request: MessageRequest):
    if not request.message:
        raise HTTPException(status_code=400, detail="Message is empty")

    return {"message": request.message}

@app.get("/")
def read_root():
    return {"message:": "Hello World"}
