#pip install google-generativeai
#https://aistudio.google.com/apikey
import google.generativeai as genai
import os
import api_keys



# Configurar o cliente da API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Carregar o modelo Gemini
model = genai.GenerativeModel("gemini-1.5-flash")

# Fazer uma pergunta ao modelo
response = model.generate_content("Explique a teoria da relatividade de forma simples.")
print(response.text)
