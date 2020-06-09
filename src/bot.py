import config
import telebot
import logging

bot = telebot.TeleBot(config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


bot.polling(none_stop=False, interval=0, timeout=20)
