from sqligther import SQLighter
import config
import telebot
from telebot import types
import logging

bot = telebot.TeleBot(config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
db = SQLighter(config.database_name)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = bot.send_video(message.chat.id, config.video_id, None)
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Нет', 'Да')
    bot.reply_to(msg, 'Хотите знать больше?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_choice_step)


def process_choice_step(message):
    chat_id = message.chat.id
    answer = message.text
    decision = ""
    if (answer == u'Да'):
        decision = f"Дорогой гость, я приглашаю тебя в чат: {config.invite_link}"
    elif (answer == u'Нет'):
        decision = "Ок, скоро мы вернемся"
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(chat_id, decision, reply_markup=markup)


bot.polling()
