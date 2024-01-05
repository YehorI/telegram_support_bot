import os

from dotenv import load_dotenv


class Config:
    load_dotenv()
    TOKEN = os.getenv("BOT_TOKEN")
    SUPPORT_CHAT_ID = int(os.getenv("SUPPORT_CHAT_ID"))