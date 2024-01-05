from aiogram import Bot
from config import Config
import threading


class TelegramBot:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(TelegramBot, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):  # Prevents initializing more than once
            self.token = Config.TOKEN
            try:
                self._bot = Bot(self.token)
            except Exception as e:
                # Add appropriate logging and error handling
                # Consider what should happen if bot fails to initialize
                raise ValueError("Failed to initialize the bot") from e
            self.initialized = True

    @property
    def bot(self):
        return self._bot

