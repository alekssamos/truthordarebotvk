import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

dburl = os.getenv("dburl", "sqlite+aiosqlite:///"+"db.sqlite3")
maxplayers = int(os.getenv("maxplayers", 10))
recruitmentendtimeminute = int(os.getenv("recruitmentendtimeminute", 5))
