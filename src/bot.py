# -*- coding: utf-8 -*-

import sentry_sdk
import time
import telebot
import logging
import phonenumbers
from telebot import types
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type
import config
from postgretor import Postgretor

bot = telebot.TeleBot(config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
user_dict = {}
conn = Postgretor()

sentry_sdk.init(
    "https://28251dceb1e74021a30190263a96196d@o406290.ingest.sentry.io/5273457")


class User:
    def __init__(self, language):
        self.language = language
        self.username = None
        self.telegram_id = None
        self.name = None
        self.city = None
        self.phone_number = None
        self.decision = False


class Error(Exception):
    """Base class for other exceptions"""
    pass


class PhoneExists(Error):
    pass


languages = {'cb_ru': f"Русский 🇷🇺️", 'cb_kz': "Қазақша 🇰🇿️"}


def gen_reply_markup(words, row_width, isOneTime, isContact):
    keyboard = types.ReplyKeyboardMarkup(
        one_time_keyboard=isOneTime, row_width=row_width, resize_keyboard=True)
    for word in words:
        keyboard.add(types.KeyboardButton(
            text=word, request_contact=isContact))
    return keyboard


def gen_inline_markup(dict, row_width):
    markup = types.InlineKeyboardMarkup()
    markup.row_width = row_width
    buttons = []
    for key in dict:
        buttons.append(types.InlineKeyboardButton(
            text=dict[key], callback_data=key))
    if row_width == 0:
        for button in buttons:
            markup.add(button)
    else:
        markup.add(*buttons)
    return markup


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, 'Здравствуйте, это телеграм бот потребительского кооператива "Елимай-2019". Выберите язык на котором хотите продолжить переписку',
                           reply_markup=gen_inline_markup(languages, 2))


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data in ("cb_ru", "cb_kz"):
        if call.data == "cb_ru":
            user = User('ru')
            user_dict[chat_id] = user
            bot.answer_callback_query(call.id, "Выбран русский язык")
        elif call.data == "cb_kz":
            user = User('kz')
            user_dict[chat_id] = user
            bot.answer_callback_query(call.id, "Қазақша тілі таңдалды")
        user = user_dict[chat_id]
        user.username = call.message.chat.username
        user.telegram_id = str(call.message.chat.id)
        bot.send_message(chat_id, 'VIDEO WILL BE THIS')
        time.sleep(3)
        choices = {'cb_yes': config.localization[user_dict[chat_id].language]['yes'],
                   'cb_no': config.localization[user_dict[chat_id].language]['no'], }
        bot.send_message(chat_id, config.localization[user_dict[chat_id].language]
                         ['offer'], reply_markup=gen_inline_markup(choices, 2))
    elif call.data == "cb_no":
        user = user_dict[chat_id]
        try:
            bot.edit_message_text(
                config.localization[user.language]['deny'], chat_id, call.message.message_id)
            bot.answer_callback_query(
                call.id, config.localization[user.language]['no'])
            if not conn.exist_user(str(chat_id)):
                tpl = (user.name, user.city, user.phone_number,
                       user.language, user.telegram_id, user.username, user.decision)
                res = conn.add_user(tpl)
        except Exception as e:
            pass
    elif call.data == "cb_yes":
        try:
            user = user_dict[chat_id]
            user.decision = True
            bot.answer_callback_query(
                call.id, config.localization[user.language]['yes'])
            if conn.exist_user(user.telegram_id) and conn.select_user(user.telegram_id)[7]:
                res = conn.select_user(user.telegram_id)
                bot.send_message(chat_id, 'Пользователь уже зарегестрирован')
            else:
                msg = bot.send_message(
                    chat_id, config.localization[user.language]['name'])
                bot.register_next_step_handler(msg, process_name_step)
        except Exception as e:
            bot.reply_to(message, 'oooops')
    elif call.data[0] == 'c':
        city = int(call.data[1])
        user = user_dict[chat_id]
        user.city = city
        buttons = (config.localization[user.language]['send_contact'],)
        msg = bot.send_message(
            chat_id, config.localization[user.language]['number'], reply_markup=gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    user = user_dict[chat_id]
    user.name = name
    res = conn.select_cities()
    cities = []
    lang = 3 if user.language == "kz" else 2
    for i in range(len(res)):
        cities.append(res[i][lang])
    callbacks = []
    for i in range(len(res)):
        callbacks.append('c'+str(res[i][0]))
    cities = dict(zip(callbacks, cities))
    msg = bot.send_message(
        chat_id, f"{user.name}, {config.localization[user.language]['city']}", reply_markup=gen_inline_markup(cities, 1))


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if message.contact:
            user.phone_number = message.contact.phone_number
        else:
            number = message.text
            if not (carrier._is_mobile(number_type(phonenumbers.parse(number)))):
                raise Exception
            user.phone_number = number
        if conn.exist_phone(user.phone_number):
            raise PhoneExists
        options = [config.localization[user.language]['no'],
                   config.localization[user.language]['yes']]
        lang = 3 if user.language == "kz" else 2
        city_name = conn.select_city(user.city)[0][lang]
        bot.send_message(chat_id, f'Имя: {user.name}\n'
                         f'Номер: {user.phone_number}\n'
                         f'Город: {city_name}')
        msg = bot.send_message(
            chat_id, config.localization[user.language]['confirm'], reply_markup=gen_reply_markup(options, 1, True, False))
        bot.register_next_step_handler(msg, process_confirmation_step)
    except PhoneExists:
        msg = bot.send_message(
            message.chat.id, config.localization[user.language]['number_exists'], reply_markup=gen_reply_markup([], 1, False, False))
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception:
        buttons = (config.localization[user.language]['send_contact'],)
        msg = bot.send_message(
            message.chat.id, config.localization[user.language]['number_invalid'], reply_markup=gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def process_confirmation_step(message):
    try:
        chat_id = message.chat.id
        confirm = message.text
        user = user_dict[chat_id]
        markup = types.ReplyKeyboardRemove(selective=False)
        if confirm in ('Да', 'Йә'):
            if conn.exist_user(user.telegram_id) and not conn.select_user(user.telegram_id)[7]:
                tpl = [user.name, user.city, user.phone_number,
                       user.language, user.decision, user.telegram_id]
                conn.update_user(tpl)
            else:
                tpl = (user.name, user.city, user.phone_number, user.language,
                       user.telegram_id, user.username, user.decision)
                res = conn.add_user(tpl)
            lang = 3 if user.language == "kz" else 2
            bot.send_message(-414383943, f'Имя: {user.name}\n'
                             f'Номер: {user.phone_number}\n'
                             f'Город: {conn.select_city(user.city)[0][lang]}', reply_markup=markup)
        elif confirm in ('Нет', 'Жоқ'):
            decision = config.localization[user.language]['cancel_registration']
            bot.send_message(chat_id, decision, reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.polling()
