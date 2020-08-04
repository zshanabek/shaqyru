import os
import telebot
import logging
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))
DEV_MODE = True if os.getenv("ENV") == "DEVELOPMENT" else False
telebot.logger.setLevel(logging.DEBUG)
