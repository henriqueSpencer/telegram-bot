from pydantic import BaseModel

class MessageRequest(BaseModel):
    chat_id: int
    text: str

class MessageResponse(BaseModel):
    chat_id: int
    reply: str