import config
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate



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
        mensagem_teste = "Gastei 100 reais no Uber hoje."

        is_expense = self.chain_identificar.run(mensagem_teste)
        amount = self.chain_amount.run(mensagem_teste)
        category = self.chain_category.run(mensagem_teste)
        return {
            "is_expense": bool(is_expense) if is_expense != "null" else None,
            "amount": float(amount) if amount != "null" else None,
            "category": category,
        }

class Message:
    def __init__(self, texto: str, user_id: int):
        """
        Class to represent one mensage
        """
        self.texto = texto
        self.user_id = user_id
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
        elif amount is None and category is None:
            msg_returned = "is been impossible to retrieve: "
            if amount is None:
                msg_returned += "the value from your expenditures,"
            if amount is None:
                msg_returned += "the category from your expenditures, "
            raise ValueError(f"{msg_returned}\n please improve the text and send again.")

    def check_user(self):
        return DBmanager().select_user(self.user_id)

class DBmanager:
    def __init__(self):
        pass

    def save(self, message):
        # caso qualquer erro, raise exption
        pass

    def get(self, user_id):
        pass

    def update(self, message):
        pass

    def delete(self, user_id):
        pass

    def select_user(self, user_id):
        users = [1234, 3333,2900]
        if user_id in users:
            return True
        return False

if __name__ == '__main__':

    from picklefy import PickleFy
    try:
        msg = Message("ola", 1234)
        if not msg.check_user():
            raise ValueError("User not found")

        # llm = GeminiPipeline()
        # info = llm.run_all(msg.texto)
        # PickleFy().serialize(file_name='info', variavel=info)

        info = PickleFy().serialize(file_name='info')
        try:
            msg.definir_despesa(info['is_expense'], info['amount'], info['category'])
        except ValueError as e:
            raise e
        try:
            db = DBmanager()
            db.save(msg)
        except Exception as e:
            e.message = f"Error to save the message: {e.message}"
            raise e

        # send telegram mensage with the success
        # "[Category] expense added ✅"
    except Exception as e:
        # send telegram mensage with the error
        pass
