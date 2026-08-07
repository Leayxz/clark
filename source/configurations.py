import os
from dotenv import load_dotenv

load_dotenv()

class APILNMarkets:
    API_KEY = os.environ["API_KEY"]
    API_SECRET = os.environ["API_SECRET"]
    API_PASSPHRASE = os.environ["API_PASSPHRASE"]


class Authentication:
    AUTHORIZATION_SECRET_KEY = os.environ["AUTHORIZATION_SECRET_KEY"]


class TelegramKeys:
    TELEBOT = os.environ["TELEBOT"]
    CHAT_ID = os.environ["CHAT_ID"]
