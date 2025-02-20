from fastapi import APIRouter, Header, HTTPException
from app.api.v1.schemas.message import MessageResponse, MessageRequest
import os


router = APIRouter()


@router.post("/", response_model=MessageResponse)
async def message_process(request: MessageRequest, api_key: str = Header(None)):
    """
        Processes an incoming message and returns a response.

        - **request**: Contains message data (chat_id and text).
        - **api_key**: API key provided in the request header.
    """
    API_KEY = os.getenv("API_KEY")
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="🔒 Access denied: Invalid API Key.")

    chat_id = request.chat_id
    text = request.text

    # 🚀 Simulated expense processing logic
    if "spent" in text.lower() or "bought" in text.lower():
        reply = f"📊 It looks like you're logging an expense: '{text}'"
    else:
        reply = f"🤖 I received your message: '{text}'"

    return {"chat_id": chat_id, "reply": reply}

