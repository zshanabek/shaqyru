# -*- coding: utf-8 -*-
import os
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
from dotenv import load_dotenv

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, '.env'))
user_dict = {}
conn = Postgretor()
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

if os.getenv("ENV") == "DEVELOPMENT":
    logger = telebot.logger
    telebot.logger.setLevel(logging.DEBUG)

if os.getenv("ENV") != "DEVELOPMENT":
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
    markup = types.ReplyKeyboardMarkup(
        one_time_keyboard=isOneTime, row_width=row_width, resize_keyboard=True)
    buttons = []
    for word in words:
        buttons.append(types.KeyboardButton(
            text=word, request_contact=isContact))
    if row_width == 0:
        for b in buttons:
            markup.add(b)
    else:
        markup.add(*buttons)
    return markup


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
    try:
        chat_id = message.chat.id
        if (message.chat.type == "private"):
            bot.send_message(chat_id, 'Здравствуйте, это телеграм бот потребительского кооператива "Елимай-2019". Выберите язык на котором хотите продолжить переписку',
                             reply_markup=gen_inline_markup(languages, 2))
        else:
            bot.send_message(chat_id, "Бот работает в личном чате")
    except Exception as e:
        bot.reply_to(message, 'oooops')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data in ("cb_ru", "cb_kz"):
        language = 'kz' if call.data == 'cb_kz' else 'ru'
        user = User(language)
        user_dict[chat_id] = user
        bot.answer_callback_query(
            call.id, config.l10n[user.language]['language'])
        # video = open(
        # '/home/sam/Documents/Projects/bots/shaqyru/video/promo_ru.mp4', 'rb')
        video = 'VIDEO_ID_KZ' if language == 'kz' else 'VIDEO_ID_RU'
        bot.send_video(chat_id, os.getenv(
            video), caption=config.l10n[user.language]['video'])
        user.username = call.message.chat.username
        user.telegram_id = str(call.message.chat.id)
        if os.getenv("ENV") != "DEVELOPMENT":
            time.sleep(7)
        choices = {'cb_yes': config.l10n[user.language]['yes'],
                   'cb_no': config.l10n[user.language]['no'], }
        bot.send_message(chat_id, config.l10n[user.language]
                         ['offer'], reply_markup=gen_inline_markup(choices, 2))
    elif call.data in ("cb_no", "cb_yes"):
        if call.data == "cb_no":
            user = user_dict[chat_id]
            try:
                bot.edit_message_text(
                    config.l10n[user.language]['deny'], chat_id, call.message.message_id)
                bot.answer_callback_query(
                    call.id, config.l10n[user.language]['no'])
                if not conn.exist_user(str(chat_id)):
                    tpl = (user.name, user.city, user.phone_number,
                           user.language, user.telegram_id, user.username, user.decision)
                    res = conn.add_user(tpl)
            except Exception as e:
                bot.reply_to(call.message, 'oooops')
        else:
            try:
                user = user_dict[chat_id]
                user.decision = True
                bot.answer_callback_query(
                    call.id, config.l10n[user.language]['yes'])
                if conn.exist_user(user.telegram_id) and conn.select_user(user.telegram_id)[7]:
                    res = conn.select_user(user.telegram_id)
                    bot.send_message(
                        chat_id, config.l10n[user.language]['already_registered'])
                else:
                    msg = bot.send_message(
                        chat_id, config.l10n[user.language]['name'])
                    bot.register_next_step_handler(msg, process_name_step)
            except Exception as e:
                bot.reply_to(call.message, 'oooops')
    else:
        city = int(call.data.split('_')[-1])
        user = user_dict[chat_id]
        user.city = city
        buttons = (config.l10n[user.language]['send_contact'],)
        msg = bot.send_message(
            chat_id, config.l10n[user.language]['number'], reply_markup=gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = user_dict[chat_id]
        user.name = name
        res = conn.select_cities()
        cities = []
        lang = 2 if user.language == "kz" else 3
        for i in range(len(res)):
            cities.append(res[i][lang])
        callbacks = []
        for i in range(len(res)):
            callbacks.append('cb_city_'+str(res[i][0]))
        cities = dict(zip(callbacks, cities))
        msg = bot.send_message(
            chat_id, f"{user.name}, {config.l10n[user.language]['city']}", reply_markup=gen_inline_markup(cities, 1))
    except Exception as e:
        bot.reply_to(message, 'oooops')


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
        options = [config.l10n[user.language]['no'],
                   config.l10n[user.language]['yes']]
        lang = 2 if user.language == "kz" else 3
        city_name = conn.select_city(user.city)[0][lang]
        bot.send_message(chat_id, f'{config.l10n[user.language]["name_single"]}: {user.name}\n'
                         f'{config.l10n[user.language]["number_single"]}: {user.phone_number}\n'
                         f'{config.l10n[user.language]["city_single"]}: {city_name}')
        msg = bot.send_message(
            chat_id, config.l10n[user.language]['confirm'], reply_markup=gen_reply_markup(options, 2, True, False))
        bot.register_next_step_handler(msg, process_confirmation_step)
    except PhoneExists:
        msg = bot.send_message(
            message.chat.id, config.l10n[user.language]['number_exists'], reply_markup=gen_reply_markup([], 1, False, False))
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception:
        buttons = (config.l10n[user.language]['send_contact'],)
        msg = bot.send_message(
            message.chat.id, config.l10n[user.language]['number_invalid'], reply_markup=gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def process_confirmation_step(message):
    try:
        chat_id = message.chat.id
        confirm = message.text
        user = user_dict[chat_id]
        markup = types.ReplyKeyboardRemove(selective=False)
        if confirm in ('Да', 'Йә'):
            id = None
            if conn.exist_user(user.telegram_id) and not conn.select_user(user.telegram_id)[7]:
                tpl = [user.name, user.city, user.phone_number,
                       user.language, user.decision, user.telegram_id]
                id = conn.update_user(tpl)
            else:
                tpl = (user.name, user.city, user.phone_number, user.language,
                       user.telegram_id, user.username, user.decision)
                if not conn.exist_user(user.telegram_id):
                    id = conn.add_user(tpl)
            lang = 3
            bot.send_message(os.getenv("GROUP_CHAT_ID"),
                             f'ID: {id}\n'
                             f'Имя: {user.name}\n'
                             f'Номер: {user.phone_number}\n'
                             f'Город: {conn.select_city(user.city)[0][lang]}\n'
                             f'Язык: {user.language}', disable_notification=True)
            bot.send_message(
                chat_id, config.l10n[user.language]['success_registration'], reply_markup=markup)
        elif confirm in ('Нет', 'Жоқ'):
            decision = config.l10n[user.language]['cancel_registration']
            bot.send_message(chat_id, decision, reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.polling()
