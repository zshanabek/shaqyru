# -*- coding: utf-8 -*-
import os
import time
import sentry_sdk
import phonenumbers
from phonenumbers import carrier, parse
from telebot import types
from phonenumbers.phonenumberutil import number_type
from postgretor import Postgretor
from models import User
from exceptions import PhoneExists
import config
import utils
from settings import bot, DEV_MODE

user_dict = {}
conn = Postgretor()

if not DEV_MODE:
    sentry_sdk.init(os.getenv("SENTRY_URL"))


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    try:
        chat_id = message.chat.id
        if (message.chat.type == "private"):
            bot.send_message(chat_id, 'Здравствуйте, это телеграм бот потребительского кооператива "Елимай-2019". Выберите язык на котором хотите продолжить переписку',
                             reply_markup=utils.gen_inline_markup(config.languages, 2))
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
        #     '/home/sam/Documents/Projects/elimaiga/promo_kz.mp4', 'rb')
        # bot.send_video(chat_id, video)
        video = 'VIDEO_ID_KZ' if language == 'kz' else 'VIDEO_ID_RU'
        bot.send_video(chat_id, os.getenv(video),
                       caption=config.l10n[user.language]['video'])
        user.username = call.message.chat.username
        user.telegram_id = str(call.message.chat.id)
        if not DEV_MODE:
            time.sleep(7)
        choices = {'cb_yes': config.l10n[user.language]['yes'],
                   'cb_no': config.l10n[user.language]['no'], }
        bot.send_message(chat_id, config.l10n[user.language]
                         ['offer'], reply_markup=utils.gen_inline_markup(choices, 2))
    elif call.data in ("cb_no", "cb_yes"):
        if call.data == "cb_no":
            try:
                user = user_dict[chat_id]
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
                lang = 2 if user.language == "kz" else 3
                if conn.exist_user(user.telegram_id) and conn.select_user(user.telegram_id)[7]:
                    res = conn.select_user(user.telegram_id)
                    bot.send_message(
                        chat_id, config.l10n[user.language]['already_registered'])
                else:
                    res = conn.select_cities()
                    cities = []
                    for i in range(len(res)):
                        cities.append(res[i][lang])
                    callbacks = []
                    for i in range(len(res)):
                        callbacks.append('cb_city_'+str(res[i][0]))
                    cities = dict(zip(callbacks, cities))
                    msg = bot.send_message(
                        chat_id, f"{user.name}, {config.l10n[user.language]['city']}", reply_markup=utils.gen_inline_markup(cities, 1))
            except Exception as e:
                bot.reply_to(call.message, 'oooops')
    else:
        city = int(call.data.split('_')[-1])
        user = user_dict[chat_id]
        user.city = city
        buttons = (config.l10n[user.language]['send_contact'],)
        msg = bot.send_message(
            chat_id, config.l10n[user.language]['number'], reply_markup=utils.gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = user_dict[chat_id]
        user.name = name
        lang = 2 if user.language == "kz" else 3
        city_name = conn.select_city(user.city)[0][lang]
        bot.send_message(chat_id, f'{config.l10n[user.language]["name_single"]}: {user.name}\n'
                               f'{config.l10n[user.language]["number_single"]}: {user.phone_number}\n'
                               f'{config.l10n[user.language]["city_single"]}: {city_name}')
        save_data(message)

    except Exception as e:
        bot.reply_to(message, 'oooops')


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if message.contact:
            number = message.contact.phone_number
            # Get last 10 characters
            user.phone_number = f'8{number[-10:]}'
        else:
            number = message.text
            if not (carrier._is_mobile(number_type(parse(number)))):
                raise Exception
            user.phone_number = number
        if conn.exist_phone(user.phone_number):
            raise PhoneExists
        markup = types.ReplyKeyboardRemove(selective=False)
        msg = bot.send_message(chat_id, config.l10n[user.language]['name'], reply_markup=markup)
        bot.register_next_step_handler(msg, process_name_step)
    except PhoneExists:
        msg = bot.send_message(
            message.chat.id, config.l10n[user.language]['number_exists'], reply_markup=utils.gen_reply_markup([], 1, False, False))
        bot.register_next_step_handler(msg, process_phone_step)
    except Exception:
        buttons = (config.l10n[user.language]['send_contact'],)
        msg = bot.send_message(
            message.chat.id, config.l10n[user.language]['number_invalid'], reply_markup=utils.gen_reply_markup(buttons, 1, False, True))
        bot.register_next_step_handler(msg, process_phone_step)


def save_data(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
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
        if id is not None:
            lang = 3
            username = '' if user.username == None else f'@{user.username}'
            bot.send_message(os.getenv("GROUP_CHAT_ID"),
                             f'ID: {id}\n'
                             f'Имя: {user.name}\n'
                             f'Имя пользователя: {username}\n'
                             f'Город: {conn.select_city(user.city)[0][lang]}\n'
                             f'Номер: {user.phone_number}\n'
                             f'Язык: {user.language}', disable_notification=True)
            bot.send_message(
                chat_id, config.l10n[user.language]['success_registration'])
        del user
    except Exception as e:
        bot.reply_to(message, 'oooops')


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()
