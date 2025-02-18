#from google.auth import message
from google.auth import message
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

import google.generativeai as genai
import os
import api_keys
import json
import re


async def start(update: Update, context):
    await update.message.reply_text("Olá! Eu sou um bot simples.")


async def echo(update: Update, context):
    texto_recebido = update.message.text
    await update.message.reply_text(f"Você disse: {texto_recebido}")


def main():
    app = Application.builder().token(os.getenv("TELEGRAM_API_TOKEN")).build()

    # Adicionar comandos e respostas
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    print("Bot está rodando...")
    app.run_polling()



class Message:
    def __init__(self, texto: str, user_id: int):
        """
        Class to represent one mensage
        """
        self.texto = texto
        self.user_id = user_id
        self.is_expense = False
        self.valor = None
        self.categoria = None

    def __str__(self):
        """Retorna uma representação em string do objeto."""
        return f"Mensagem(user_id={self.user_id}, texto='{self.texto}', is_expensas={self.is_expensas}, valor={self.valor}, categoria='{self.categoria}')"

    def definir_despesa(self, valor: float, categoria: str):
        """
        Define a mensagem como uma despesa e adiciona os detalhes.

        :param valor: Valor da despesa.
        :param categoria: Categoria da despesa.
        """
        self.is_expense = True
        self.valor = valor
        self.categoria = categoria

class GeminiIA:
    def __init__(self):
        # Configurar o cliente da API
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # Carregar o modelo Gemini
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def get_expense(self, message):
        prompt = f"""
        Analise a mensagem abaixo e responda três perguntas separadamente, sempre retornando um JSON **válido**.

        Mensagem: "{message.texto}"

        Responda as seguintes perguntas:
        1. Essa mensagem contém informações de gasto? (Responda com `true` ou `false`).
        2. Se sim, retorne o valor do gasto identificado. Se não houver gasto, retorne `null`.
        3. Se sim, retorne a categoria correspondente entre as seguintes opções:
           ["Housing", "Transportation", "Food", "Utilities", "Insurance", "Medical/Healthcare", "Savings",
           "Debt", "Education", "Entertainment", "Other"]. Se não houver gasto, retorne `null`.

        ### **IMPORTANTE:**  
        - A resposta **DEVE** ser **exclusivamente** um JSON **válido**, sem texto adicional.
        - **Formato exato da resposta:**

        {{
            "resposta1": true/false,
            "resposta2": número ou null,
            "resposta3": "categoria" ou null
        }}

        Responda **apenas** com este JSON, sem explicações ou texto adicional.
        """

        # Fazer uma pergunta ao modelo
        response = self.model.generate_content(prompt)
        print(response.text)
        # Converter a resposta para JSON
        try:
            respostas = json.loads(re.sub(r'```json|```', '', response.text).strip())
            message.is_expense = respostas["resposta1"]
            message.valor = respostas["resposta2"]
            message.categoria = respostas["resposta3"]
        except json.JSONDecodeError:
            print("Erro ao processar a resposta:", response.text)

        return message

class DBManager:
    def __init__(self):
        pass
    def insert(self, message):
        pass

if __name__ == "__main__":
    #main()
    mensage_obj = Message("5 reais no transporte de seu zeca", 1234)
    gen_app = GeminiIA()
    mensage_obj = gen_app.get_expense(mensage_obj)
    DBManager().insert(message)
    # If mensagem inserida e tudo ok, return mensagem inserida
    # else menssagem deu erro e o porque?
    print("End")

    # Precisa verificar se o usuario da mensagem esta no BD
    # Destinguir mensagens de gasto das comuns
    # categorizar o gasto
    """
    ● Python 3.8+ required.
    ● Must handle concurrent requests.
    ● Use LangChain with a supported LLM.
    ● PostgreSQL database.
    """
