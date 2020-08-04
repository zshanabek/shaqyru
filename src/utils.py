from telebot import types


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
