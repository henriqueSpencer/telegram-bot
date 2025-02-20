from fastapi import FastAPI
from app.api.v1.endpoints.message import router as message_router
import config

app = FastAPI(
    title="Message Processing API",
    description="API to process expenses messages",
    version="1.0.0",
)
app.include_router(
    message_router,
    prefix="/api/v1/message",
    tags=["message"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)