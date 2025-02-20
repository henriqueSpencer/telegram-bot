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
        self.prompt_identify = PromptTemplate.from_template(
            "Does this message contain an expense (Respond with `True` or `False`)? {message}")
        self.prompt_amount = PromptTemplate.from_template(
            "If there is an expense in the message '{message}', what is the amount (just the number)? Otherwise, return `null`.")
        self.prompt_category = PromptTemplate.from_template("""
        Given the following message: "{message}"
        Which category best fits? Choose from:
        Housing, Transportation, Food, Utilities, Insurance, Medical/Healthcare, Savings, Debt, Education, Entertainment, Other.
        If none fit, return `null`.
        """)

        self.chain_identify = LLMChain(llm=self.llm, prompt=self.prompt_identify)
        self.chain_amount = LLMChain(llm=self.llm, prompt=self.prompt_amount)
        self.chain_category = LLMChain(llm=self.llm, prompt=self.prompt_category)

    async def run_all(self, message: str):
        """
        Run all Gemini chains to process the message.
        """
        is_expense = await self.chain_identify.arun(message)
        amount = await self.chain_amount.arun(message)
        category = await self.chain_category.arun(message)

        return {
            "is_expense": True if is_expense == "True" else False,
            "amount": float(amount) if amount != "null" else None,
            "category": str(category) if category != "null" else None,
        }