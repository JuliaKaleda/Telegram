import telebot
from telebot import types
import itertools
import json
# https://t.me/ConfactionaryBot
bot = telebot.TeleBot('5204547877:AAECtMbKkix3DwA8BkdG3-UzM7yQECYZYSw')

def get_all_buttons():
    with open('menu.json', encoding='utf-8') as config:
        config_data = json.load(config)
    all_buttons = []
    for keyboard in config_data:
        for button in keyboard['buttons']:
            all_buttons.append(button)
    return all_buttons

def get_keyboard(keyboard_type):
    with open('menu.json', encoding='utf-8') as config:
        config_data = json.load(config)
    kb_info = list(filter(lambda el: el['keyboard_name'] == keyboard_type, config_data))[0]
    buttons = sorted(kb_info['buttons'], key=lambda el: int(el['position']))
    keyboard = types.InlineKeyboardMarkup()
    chunked = list(itertools.zip_longest(*[iter(buttons)]*3))
    for chunk in chunked:
        chunked_btn = []
        for button in list(filter(lambda el: el is not None, chunk)):
            chunked_btn.append(types.InlineKeyboardButton(button['name'], callback_data=button['id']))
        if len(chunked_btn) == 1:
            keyboard.row(chunked_btn[0])
        elif len(chunked_btn) == 2:
            keyboard.row(chunked_btn[0], chunked_btn[1])
        elif len(chunked_btn) == 3:
            keyboard.row(chunked_btn[0], chunked_btn[1], chunked_btn[2])
    return keyboard

def generate_message(button):
    msg = ''
    if 'size' in button or 'price' in button:
        msg += '<b>Десерт: %s </b>\n' % button['name']
    if 'size' in button:
        msg += '<b>Размер порции: %s г.</b>\n\n' % button['size']
    msg += button['to_print'] + '\n'
    if 'price' in button:
        msg += '\n\n'
        msg += '<b>Цена: %s</b>' % str(button['price'])
    return msg

@bot.message_handler(commands=['start'])
def start(message):
    print('Добро пожаловать, %s!' % message.from_user.full_name)
    bot.send_message(message.chat.id, 'Добро пожаловать, %s!' % message.from_user.full_name,
                     reply_markup=get_keyboard('main'))

@bot.callback_query_handler(func=lambda call: True)
def keyboard_answer(call):
    button = list(filter(lambda btn: call.data == btn['id'], get_all_buttons()))[0]
    bot.send_message(
        chat_id=call.message.chat.id,
        text=generate_message(button),
        reply_markup=get_keyboard(button['next_keyboard']),
        parse_mode='html'
    )

bot.infinity_polling()