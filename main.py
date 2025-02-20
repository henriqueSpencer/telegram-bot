
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import os
import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from picklefy import PickleFy

import pg8000
from contextlib import contextmanager




class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(os.getenv("TELEGRAM_API_TOKEN")).build()

    def main(self):
        self.app = Application.builder().token(os.getenv("TELEGRAM_API_TOKEN")).build()

        # Adicionar comandos e respostas
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.echo))

        print("Bot está rodando...")
        self.app.run_polling()

    async def start(self, update: Update, context):
        """
        Função para responder ao comando /start.
        :param update:
        :param context:
        :return:
        """
        await update.message.reply_text("Olá! Eu sou um bot simples.")

    async def echo(self, update: Update, context):
        """
        Função para responder com o mesmo texto recebido.
        :param update:
        :param context:
        :return:
        """
        try:
            menssage_text = update.message.text
            message_id = update.message.message_id
            user_name = update.message.chat.full_name
            chat_id = update.message.chat.id
            msg = handler_message(menssage_text, chat_id)
            await update.message.reply_text(f"{msg.category} expense added ✅")
        except ValueError as e:
            # send telegram mensage with the error
            await update.message.reply_text(str(e))

class GeminiPipeline:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )
        # Criar três sub-prompts separados
        prompt_identificar = PromptTemplate.from_template(
            "Essa mensagem contém um gasto (Responda com `True` ou `False`)? {mensagem}")
        prompt_amount = PromptTemplate.from_template(
            "Se houver um gasto na mensagem '{mensagem}', qual é o amount(apenas o numero)? senao retorn `null`")
        prompt_category = PromptTemplate.from_template("""
        Dada a seguinte mensagem: "{mensagem}"
        Qual category melhor se encaixa? Escolha entre:
        Housing, Transportation, Food, Utilities, Insurance, Medical/Healthcare, Savings, Debt, Education, Entertainment, Other.
        caso nao se encaixe em nenhuma retorn null
        """)

        # Criar Chains separadas
        self.chain_identificar = LLMChain(llm=self.llm, prompt=prompt_identificar)
        self.chain_amount = LLMChain(llm=self.llm, prompt=prompt_amount)
        self.chain_category = LLMChain(llm=self.llm, prompt=prompt_category)

    def run_all(self, message):

        is_expense = self.chain_identificar.run(message)
        amount = self.chain_amount.run(message)
        category = self.chain_category.run(message)
        return {
            "is_expense": True if is_expense == "True" else False,
            "amount": float(amount) if amount != "null" else None,
            "category": str(category) if category != "null" else None,
        }

class Message:
    def __init__(self, texto: str, chat_id: int):
        """
        Class to represent one mensage
        """
        self.texto = texto
        self.chat_id = chat_id
        self.user_id = None
        self.is_expense = False
        self.amount = None
        self.category = None

    def __str__(self):
        """Retorna uma representação em string do objeto."""
        return f"Mensagem(user_id={self.user_id}, texto='{self.texto}', is_expensas={self.is_expensas}, amount={self.amount}, category='{self.category}')"

    def definir_despesa(self, is_expense: bool, amount: float, category: str):
        """
        Define a mensagem como uma despesa e adiciona os detalhes.

        :param amount: amount da despesa.
        :param category: Categoria da despesa.
        """
        self.check_mensage(is_expense, amount, category)
        self.is_expense = True
        self.amount = amount
        self.category = category

    def check_mensage(self, is_expense: bool, amount:float, category:str):
        if not is_expense:
            raise ValueError("this is not a bill.")
        elif amount is None or category is None:
            # TODO: improve this mensage
            """It has been impossible to retrieve the value 
            and category from your expenditures. 
            Please refine the text and send it again."""
            msg_returned = "is been impossible to retrieve: "
            if amount is None:
                msg_returned += "the value from your expenditures,"
            if amount is None:
                msg_returned += "the category from your expenditures, "
            raise ValueError(f"{msg_returned}\n please improve the text and send again.")



    def check_user(self):
        user_exist = DBmanager().check_user(self.chat_id)
        if not user_exist:
            return False
        self.user_id = DBmanager().get_userid_by_chatid(self.chat_id)
        return True


class DBmanager:
    def __init__(self):
        # Configurações de conexão com o banco de dados
        self.config_connection = {
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'database': "telegram_bot_bd",
            'host': 'localhost',
            'port': 5432
        }

    @contextmanager
    def gerenciador_conexao_pg8000(self):
        """
        Gerenciador de contexto para conexão com o banco de dados.
        """
        conn = None
        cursor = None
        try:
            # Abrir a conexão
            conn = pg8000.connect(**self.config_connection)
            cursor = conn.cursor()
            yield cursor  # Retorna o cursor para uso dentro do bloco 'with'
            conn.commit()  # Confirma as alterações no banco de dados
        except Exception as e:
            if conn:
                conn.rollback()  # Desfaz as alterações em caso de erro
            raise e
        finally:
            # Fechar o cursor e a conexão
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def select_expenses(self, user_id):
        """
        Seleciona despesas no bd
        """
        try:
            with self.gerenciador_conexao_pg8000() as cursor:
                # Executar a query para buscar o usuário
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                resultado = cursor.fetchone()
                return resultado is not None  # Retorna True se o usuário existir
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return False

    def insert_expense(self, message):
        """
        insert expense in the db
        """
        try:
            with self.gerenciador_conexao_pg8000() as cursor:

                # Inserir os dados na tabela
                cursor.execute(
                    "INSERT INTO expenses (user_id, description, amount, category) VALUES (%s, %s, %s, %s)",
                    (message.user_id, message.texto, message.amount, message.category)
                )

        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return False

    def check_user(self, telegram_id):
        """
        Verifica se um usuário existe no banco de dados e retorna seus dados.
        """
        try:
            with self.gerenciador_conexao_pg8000() as cursor:
                # Executar a query para buscar o usuário
                #cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE telegram_id = %s)", (telegram_id,))
                resultado = cursor.fetchone()
                return resultado[0]  # Retorna os dados do usuário
        except Exception as e:
            print(f"Erro ao verificar usuário: {e}")
            return False

    def get_userid_by_chatid(self, telegram_id):
        """
        Verifica se um usuário existe no banco de dados e retorna seus dados.
        """
        try:
            with self.gerenciador_conexao_pg8000() as cursor:
                # Executar a query para buscar o usuário
                #cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
                resultado = cursor.fetchone()
                return resultado[0]  # Retorna os dados do usuário
        except Exception as e:
            print(f"Erro ao verificar usuário: {e}")
            return False


def handler_message(menssage_text, telegram_id):
    msg = Message(menssage_text, telegram_id)
    if not msg.check_user():
        raise ValueError("User not found")

    llm = GeminiPipeline()
    info = llm.run_all(msg.texto)
    # PickleFy().serialize(file_name='info', variavel=info)

    # info = PickleFy().serialize(file_name='info')
    try:
        msg.definir_despesa(info['is_expense'], info['amount'], info['category'])
    except ValueError as e:
        raise e
    try:
        db = DBmanager()
        db.insert_expense(msg)
    except Exception as e:
        e.message = f"Error to save the message: {e.message}"
        raise e

    return msg


if __name__ == "__main__":
    tg_bot = TelegramBot()
    tg_bot.main()

