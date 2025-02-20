import os
from contextlib import contextmanager
import pg8000

class DBManager:
    def __init__(self):
        # Database connection settings
        self.connection_config = {
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'database': "telegram_bot_bd",
            'host': 'localhost',
            'port': 5432
        }

    @contextmanager
    def pg8000_connection_manager(self):
        """
        Context manager for database connection.
        """
        conn = None
        cursor = None
        try:
            # Open the connection
            conn = pg8000.connect(**self.connection_config)
            cursor = conn.cursor()
            yield cursor  # Return the cursor for use within the 'with' block
            conn.commit()  # Commit changes to the database
        except Exception as e:
            if conn:
                conn.rollback()  # Rollback changes in case of an error
            raise e
        finally:
            # Close the cursor and connection
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    def select_expenses(self, user_id):
        """
        Select expenses from the database.
        """
        try:
            with self.pg8000_connection_manager() as cursor:
                # Execute the query to fetch the user
                cursor.execute("SELECT * FROM expenses WHERE user_id = %s", (user_id,))
                result = cursor.fetchall()
                return result  # Return the list of expenses
        except Exception as e:
            print(f"Error fetching expenses: {e}")
            return []

    def insert_expense(self, message):
        """
        Insert an expense into the database.
        """
        try:
            with self.pg8000_connection_manager() as cursor:
                # Insert data into the table
                cursor.execute(
                    "INSERT INTO expenses (user_id, description, amount, category) VALUES (%s, %s, %s, %s)",
                    (message.user_id, message.text, message.amount, message.category)
                )
        except Exception as e:
            print(f"Error inserting expense: {e}")
            return False

    def check_user(self, telegram_id):
        """
        Check if a user exists in the database and return their data.
        """
        try:
            with self.pg8000_connection_manager() as cursor:
                # Execute the query to check the user
                cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE telegram_id = %s)", (telegram_id,))
                result = cursor.fetchone()
                user_exist = result[0]
                if not user_exist:
                    return False
                return True
        except Exception as e:
            print(f"Error checking user: {e}")
            return False

    def get_user_id_by_telegram_id(self, telegram_id):
        """
        Get user ID by Telegram ID.
        """
        try:
            with self.pg8000_connection_manager() as cursor:
                # Execute the query to fetch the user ID
                cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
                result = cursor.fetchone()
                return result[0] if result else None  # Return the user ID if found
        except Exception as e:
            print(f"Error fetching user ID: {e}")
            return None

