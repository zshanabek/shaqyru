from sqligther import SQLighter
import config
import telebot
from telebot import types
import logging
import phonenumbers
from phonenumbers import carrier
from phonenumbers.phonenumberutil import number_type

bot = telebot.TeleBot(config.token)
logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)
db = SQLighter(config.database_name)
user_dict = {}


class User:
    def __init__(self, language):
        self.language = language
        self.name = None
        self.city = None
        self.phone_number = None
        self.decision = None


languages = {'cb_ru': 'Русский', 'cb_kz': 'Казахский'}
choices_ru = {'cb_no': 'Нет', 'cb_yes': 'Да'}
choices_kz = {'cb_no': 'Жоқ', 'cb_yes': 'Йә'}


def gen_markup(dict, row_width):
    kb = types.InlineKeyboardMarkup()
    kb.row_width = row_width
    for key in dict:
        kb.add(types.InlineKeyboardButton(
            text=dict[key], callback_data=key))
    return kb


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "cb_ru":
        user = User('ru')
        user_dict[chat_id] = user
        bot.answer_callback_query(call.id, "Выбран русский язык")
        send_video(call.message)
    elif call.data == "cb_kz":
        user = User('kz')
        user_dict[chat_id] = user
        bot.answer_callback_query(call.id, "Қазақша тілі таңдалды")
        send_video(call.message)
    elif call.data == "cb_no":
        user = user_dict[chat_id]
        user.decision = False
        try:
            bot.edit_message_text(
                config.localization[user.language]['deny'], chat_id, call.message.message_id)
        except Exception as e:
            pass
    elif call.data == "cb_yes":
        user = user_dict[chat_id]
        user.decision = True
        msg = bot.send_message(
            chat_id, config.localization[user.language]['name'])
        bot.register_next_step_handler(msg, process_name_step)
    elif call.data[0] == 'c':
        city = int(call.data[1])
        user = user_dict[chat_id]
        user.city = city
        markup = types.ReplyKeyboardMarkup()
        itembtn = types.KeyboardButton(
            'Отправить контакт', request_contact=True)
        markup.add(itembtn)
        msg = bot.send_message(
            chat_id, 'Нажмите на кнопку, чтобы поделиться телефонным номером, который привязан к этому Телеграм аккаунту. Если вы хотите указать другой номер, то введите его в формате +77021745639.', reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone_step)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id, 'Здравствуйте, это телеграм бот потребительского кооператива "Елимай-2019" Выберите язык на котором хотите продолжить разговор',
                           reply_markup=gen_markup(languages, 2))


def send_video(message):
    chat_id = message.chat.id
    bot.send_video(chat_id, config.video_id, None)
    bot.edit_message_text(config.localization[user_dict[chat_id].language]
                          ['offer'], chat_id, message.message_id, reply_markup=gen_markup(choices_ru, 2))


def process_name_step(message):
    chat_id = message.chat.id
    name = message.text
    user = user_dict[chat_id]
    user.name = name
    conn = SQLighter(config.database_name)
    res = conn.select_cities()
    lang = 0
    cities = []
    if user.language == "kz":
        lang = 1
    else:
        lang = 2
    for i in range(len(res)):
        cities.append(res[i][lang])
    callbacks = []
    for i in range(len(res)):
        callbacks.append('c'+str(res[i][0]))
    cities = dict(zip(callbacks, cities))
    msg = bot.send_message(
        chat_id, f"{user.name}, {config.localization[user.language]['city']}", reply_markup=gen_markup(cities, 2))


def process_phone_step(message):
    try:
        chat_id = message.chat.id
        user = user_dict[chat_id]
        if message.contact:
            user.phone_number = message.contact.phone_number
        else:
            number = message.text
            if (carrier._is_mobile(number_type(phonenumbers.parse(number)))):
                user.phone_number = number
        if user.phone_number == None:
            raise Exception()
        conn = SQLighter(config.database_name)
        tpl = (user.name, user.city, user.phone_number,
               user.language, user.decision)
        res = conn.add_user(tpl)
        decision = f"Дорогой гость, я приглашаю тебя в [чат]({config.invite_link})"
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(chat_id, decision,
                         reply_markup=markup, parse_mode="MarkdownV2")
    except Exception as e:
        markup = types.ReplyKeyboardMarkup()
        itembtn = types.KeyboardButton(
            'Отправить контакт', request_contact=True)
        markup.add(itembtn)
        msg = bot.send_message(
            message.chat.id, 'Что-то не похоже на нормальный номер. Если не хотите вводить номер, то проще нажать на кнопку ниже. Или же введите его в формате +77021745639.', reply_markup=markup)
        bot.register_next_step_handler(msg, process_phone_step)


bot.polling()
