
class Message:
    def __init__(self, text: str, chat_id: int):
        """
        Class to represent a message.
        :param text: full text of the message.
        :param chat_id: is the chat id of the message inside telegram.
        """
        self.text = text
        self.chat_id = chat_id
        self.user_id = None
        self.is_expense = False
        self.amount = None
        self.category = None

    def set_expense(self, is_expense: bool, amount: float, category: str):
        """
        Set the message as an expense and add details.
        :param is_expense: True if the message is an expense.
        :param amount: the amount of the expense.
        :param category: the category of the expense.
        """
        Message.check_expense(is_expense, amount, category)

        self.is_expense = True
        self.amount = amount
        self.category = category

    @staticmethod
    def check_expense(is_expense: bool, amount: float, category: str):
        """
        Check if the message is an expense and if the amount and category are not None.
        """
        if not is_expense:
            raise ValueError("this is not a bill.")
        if amount is None or category is None:
            error_msg = "Unable to retrieve: "
            if amount is None:
                error_msg += "the expense amount, "
            if category is None:
                error_msg += "the expense category, "
            error_msg += "please refine the text and try again."
            raise ValueError(error_msg)