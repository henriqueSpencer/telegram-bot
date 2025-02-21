# Telegram Bot

This is the **Bot Service** of the project, it is a service developed in **Python** using **FastAPI** and **LangChain** to process messages from Telegram users. It analyzes messages, categorizes expenses, and stores the data in a **PostgreSQL** database.

## Technologies Used

- **Python 3.8+**
- **FastAPI** for API creation
- **LangChain** for natural language processing
- **PostgreSQL** for data storage
- **SQLAlchemy** for database interaction

## Setup and Execution

### 1. Clone the Repository
```sh
git clone https://github.com/henriqueSpencer/telegram-bot.git
cd bot-service
```

### 2. Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a **.env** file in the root of the project:
```ini
GOOGLE_API_KEY = ""
TELEGRAM_API_TOKEN = ""
DB_USER = ""
DB_PASSWORD = ""
API_KEY = ""
```

### 5. Database Tables Structures
```sh
CREATE TABLE users (
"id" SERIAL PRIMARY KEY,
"telegram_id" text UNIQUE NOT NULL
);


CREATE TABLE expenses (
"id" SERIAL PRIMARY KEY,
"user_id" integer NOT NULL REFERENCES users("id"),
"description" text NOT NULL,
"amount" money NOT NULL,
"category" text NOT NULL,
"added_at" timestamp NOT null DEFAULT NOW()
);
```

### 6. Start the Server
```sh
run the main.py inside the app folder
```

The service will be available at `http://localhost:8000`.

## Project Structure

```
bot-service/
├── .env.example        # Example environment configuration
├── main.py             # Entry point
├── api/
│   ├── v1/
│   │   ├── endpoints/message.py  # Message receiving route
│   │   ├── schemas/message.py    # Validation schema
├── services/
│   ├── message_service.py  # Message processing
│   ├── gemini_service.py   # LangChain integration
├── db/
│   ├── manager.py          # Database management
│   ├── models/message.py   # Data model
```

## Workflow
1. The **Connector Service** sends messages to this service via API.
2. The message is validated, and the **telegram_id** is verified in the database.
3. The text is processed and categorized using **LangChain**.
4. The expense is stored in the **PostgreSQL** database.
5. The bot responds with the expense category and confirms the record.

## Final Considerations
- Ensure that the PostgreSQL database is running before starting the service.
- Messages should follow the format "Item Amount" (e.g., "Pizza 20 bucks").
- Detailed logs help in debugging and monitoring the service.



