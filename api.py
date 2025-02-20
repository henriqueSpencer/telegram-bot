from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

app = FastAPI()

# Defina sua API Key no arquivo .env
API_KEY = os.getenv("API_KEY")  # Exemplo: API_KEY="meu-token-seguro"

# Modelos de dados
class MessageRequest(BaseModel):
    chat_id: int
    text: str

class MessageResponse(BaseModel):
    chat_id: int
    reply: str

# Middleware para verificar a API Key
@app.post("/process-message", response_model=MessageResponse)
async def process_message(request: MessageRequest, x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=403, detail="🔒 Acesso negado: API Key inválida.")

    chat_id = request.chat_id
    text = request.text

    # 🚀 Simulated expense processing logic
    if "spent" in text.lower() or "bought" in text.lower():
        reply = f"📊 It looks like you're logging an expense: '{text}'"
    else:
        reply = f"🤖 I received your message: '{text}'"

    return {"chat_id": chat_id, "reply": reply}

# Rodar o servidor com Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
