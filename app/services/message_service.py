from app.services.gemini_service import GeminiPipeline
from app.db.manager import DBManager
from app.db.models.message import Message


async def process_message(text: str, chat_id: int):
    """
    Process a message and return a response.

    - **text**: The message text.
    - **chat_id**: The chat ID.
    """
    try:
        message = Message(text, chat_id)

        # Check if the user exists
        if not DBManager().check_user(chat_id):
            raise ValueError("User not found")

        # Process the message using Gemini
        gemini = GeminiPipeline()
        info = await gemini.run_all(message.text)

        # Validate and set expense details
        try:
            message.set_expense(info['is_expense'], info['amount'], info['category'])
        except ValueError as e:
            raise e

        # Save the expense to the database
        try:
            db = DBManager()
            message.user_id = db.get_user_id_by_telegram_id(message.chat_id)
            db.insert_expense(message)
        except Exception as e:
            e.message = f"Error to save the message: {str(e)}"
            raise e

        return {
            "chat_id": message.chat_id,
            "reply": f"{message.category} expense added ✅",
            "category": message.category,
            "amount": message.amount,
        }
    except Exception as e:
        return {
            "chat_id": message.chat_id,
            "reply": str(e),
            "category": message.category,
            "amount": message.amount,
        }