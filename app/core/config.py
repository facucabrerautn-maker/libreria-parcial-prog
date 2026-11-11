import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"
