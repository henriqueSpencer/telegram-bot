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
            "Essa mensagem contém um gasto (Responda com `true` ou `false`)? {mensagem}")
        prompt_valor = PromptTemplate.from_template(
            "Se houver um gasto na mensagem '{mensagem}', qual é o valor? senao retorn `null`")
        prompt_categoria = PromptTemplate.from_template("""
        Dada a seguinte mensagem: "{mensagem}"
        Qual categoria melhor se encaixa? Escolha entre:
        Housing, Transportation, Food, Utilities, Insurance, Medical/Healthcare, Savings, Debt, Education, Entertainment, Other.
        caso nao se encaixe em nenhuma retorn null
        """)

        # Criar Chains separadas
        self.chain_identificar = LLMChain(llm=self.llm, prompt=prompt_identificar)
        self.chain_valor = LLMChain(llm=self.llm, prompt=prompt_valor)
        self.chain_categoria = LLMChain(llm=self.llm, prompt=prompt_categoria)

    def run_all(self, message):
        mensagem_teste = "Gastei 100 reais no Uber hoje."

        identificador = self.chain_identificar.run(mensagem_teste)
        valor = self.chain_valor.run(mensagem_teste)
        categoria = self.chain_categoria.run(mensagem_teste)
        return {
            "summary": identificador,
            "analysis": valor,
            "insights": categoria,
        }

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

    def definir_despesa(self, is_expense: bool, valor: float, categoria: str):
        """
        Define a mensagem como uma despesa e adiciona os detalhes.

        :param valor: Valor da despesa.
        :param categoria: Categoria da despesa.
        """
        self.check_mensage(is_expense, valor, categoria)
        self.is_expense = True
        self.valor = valor
        self.categoria = categoria

    def check_mensage(self, is_expense, valor, categoria):
        if not is_expense:
            raise ValueError("this is not a bill.")
        elif valor is None and categoria is None:
            msg_returned = "is been impossible to retrieve: "
            if valor is None:
                msg_returned += "the value from your expenditures,"
            if valor is None:
                msg_returned += "the category from your expenditures, "
            raise ValueError(f"{msg_returned}\n please improve the text and send again.")

class db_maneger:
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

if __name__ == '__main__':


    try:
        msg = Message("ola", 1234)
        llm = GeminiPipeline()

        info = llm.run_all(msg.texto)
        try:
            msg.definir_despesa(info['identificador'], info['valor'], info['categoria'])
        except ValueError as e:
            raise e
        try:
            db = db_maneger()
            db.save(msg)
        except Exception as e:
            e.message = f"Error to save the message: {e.message}"
            raise e

    except Exception as e:
        # send telegram mensage with the error
        pass
