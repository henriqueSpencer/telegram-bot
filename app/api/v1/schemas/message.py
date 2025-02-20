from pydantic import BaseModel
from typing import Optional

class MessageRequest(BaseModel):
    chat_id: int
    text: str

class MessageResponse(BaseModel):
    chat_id: int
    reply: str
    category: Optional[str] = None
    amount: Optional[float] = None