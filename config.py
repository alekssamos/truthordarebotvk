from loguru import logger

logger.debug("config imported")
TOKEN: str = ""
dburl: str = ""
maxplayers: int = 0
recruitmentendtimeminute: int = 0
apiserver_host: str = ""
apiserver_port: int = 0
apiserver_base_url: str = ""
vk_app_id: int = 0
vk_app_secret: str = ""


def load_config():
    from os import getenv
    from dotenv import load_dotenv

    load_dotenv()

    global TOKEN, dburl, maxplayers, recruitmentendtimeminute, apiserver_host, apiserver_port, apiserver_base_url, vk_app_id, vk_app_secret
    TOKEN = getenv("TOKEN")
    dburl = getenv("dburl", "sqlite+aiosqlite:///" + "db.sqlite3")
    maxplayers = int(getenv("maxplayers", 10))
    recruitmentendtimeminute = int(getenv("recruitmentendtimeminute", 5))
    apiserver_host = getenv("apiserver_host", "127.0.0.1")
    apiserver_port = int(getenv("apiserver_port", 5000))
    apiserver_base_url = getenv("apiserver_base_url", "/")
    vk_app_id = int(getenv("vk_app_id", 0))
    vk_app_secret = getenv("vk_app_secret", "")
    logger.debug("config loaded")


load_config()
