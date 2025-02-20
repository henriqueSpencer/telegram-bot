from fastapi import APIRouter, Header, HTTPException
from app.api.v1.schemas.message import MessageResponse, MessageRequest
from app.services.message_service import process_message
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

    try:
        response = await process_message(request.text, request.chat_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

