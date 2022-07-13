from loguru import logger

logger.debug("config imported")
TOKEN: str = ""
dburl: str = ""
maxplayers: int = 0
recruitmentendtimeminute: int = 0


def load_config():
    from os import getenv
    from dotenv import load_dotenv

    load_dotenv()

    global TOKEN, dburl, maxplayers, recruitmentendtimeminute
    TOKEN = getenv("TOKEN")
    dburl = getenv("dburl", "sqlite+aiosqlite:///" + "db.sqlite3")
    maxplayers = int(getenv("maxplayers", 10))
    recruitmentendtimeminute = int(getenv("recruitmentendtimeminute", 5))
    logger.debug("config loaded")


load_config()
