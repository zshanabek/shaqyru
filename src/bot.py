from sqligther import SQLighter
import config
import telebot
from telebot import types
import logging
import os

bot = telebot.TeleBot(config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
db = SQLighter(config.database_name)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")
    bot.send_video(message.chat.id, config.video_id, None)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Нет', 'Да')
    msg = bot.reply_to(message, 'Хотите знать больше?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_choice_step)


def process_choice_step(message):
    chat_id = message.chat.id
    answer = message.text
    if (answer == u'Да'):
        positive_answer(message)

    elif (answer == u'Нет'):
        negative_answer(message)


def positive_answer(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id, f"Дорогой гость, я приглашаю тебя в чат: {config.invite_link}")


def negative_answer(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Ок, скоро мы вернемся")


bot.polling(none_stop=False, interval=0, timeout=20)
