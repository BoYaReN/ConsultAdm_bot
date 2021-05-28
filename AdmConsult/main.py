import telebot
from telebot import types

from enums import *
import config
from database import *


bot: telebot.TeleBot = telebot.TeleBot(config.TOKEN)
me: telebot.types.User = bot.get_me()


class User:
    def __init__(self, tg_id, username):
        self.tg_id = tg_id
        self.username = username
        self.state = State()
        self.send = Send()


class State:
    def __init__(self):
        self.send = False
        self.reg_form = 0
        self.send_admin = 0

class Send:
    def __init__(self):
        self.id = {}

user_dict: dict[int, User] = {}


@bot.message_handler(commands=['start', 'return'])
def welcome(message: types.Message):
    sender: types.User = message.from_user
    chat_id = message.chat.id
    user_dict[chat_id] = User(sender.id, sender.username)

    user_dict[chat_id].state.reg_form = 0
    user_dict[chat_id].state.send = False
    user_dict[chat_id].state.send_admin = 0

    if message.chat.type != chat_types.private:
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if chat_id == config.DEVELOPER_ID:
        markup.add(
            types.KeyboardButton('Написати в підтримку 📩'),
            types.KeyboardButton('Залишити Анкету 🧾'),
            types.KeyboardButton('Написати листа 📤')
        )
    else:
        markup.add(
            types.KeyboardButton('Написати в підтримку 📩'),
            types.KeyboardButton('Залишити Анкету 🧾')
        )

    text = 'Вас вітає підтримка приймальної комісії.'
    bot.send_message(message.chat.id, text, reply_markup=markup)


@bot.message_handler(content_types=['text'])
def consult_message(message: types.Message):
    sender: types.User = message.from_user
    chat_id = message.chat.id

    if chat_id not in user_dict:
        user_dict[chat_id] = User(sender.id, sender.username)


    if message.text == 'Написати в підтримку 📩':
        user_dict[chat_id] = User(sender.id, sender.username)
        user_dict[chat_id].state.send = True

        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup1.add(
            types.KeyboardButton('/return')
        )
        bot.reply_to(message, 'Напишіть ваше повідомлення відправте його боту, а після цього натисніть на кнопку '
                              '"Відправити". Підтримка незабаром відповість вам.', reply_markup=markup1)

    elif message.text == 'Залишити Анкету 🧾':
        user_dict[chat_id] = User(sender.id, sender.username)
        user_dict[chat_id].state.reg_form = 1

        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup1.add(
            types.KeyboardButton('/return')
        )
        bot_response = bot.reply_to(message, 'Вкажіть ваше імя:', reply_markup=markup1)

        person, created = Person.get_or_create(telegram_id=sender.id)

    elif chat_id == config.DEVELOPER_ID and message.text == 'Написати листа 📤':
        user_dict[chat_id].state.send_admin = 1
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup1.add(
            types.KeyboardButton('/return')
        )
        bot.send_message(message.chat.id, 'Вкажіть id користувача якому хочете відправити повідомлення:',
                         reply_markup=markup1)


    elif user_dict[chat_id].state.send == True:
        message_consult = f'{message.chat.id} @{sender.username}, {message.text}'

        bot.send_message(config.DEVELOPER_ID, message_consult)
        user_dict[chat_id].state.send = False
        bot.send_message(message.chat.id, 'Ваш лист відправленно. Незабаром підтримка відповість вам!')

    elif user_dict[chat_id].state.reg_form == 1:
        person = Person.get(telegram_id=sender.id)
        person.first_name = message.text
        person.save()

        user_dict[chat_id].state.reg_form = 2
        bot.send_message(message.chat.id, 'Вкажіть вашу фамілію:')

    elif user_dict[chat_id].state.reg_form == 2:
        person = Person.get(telegram_id=sender.id)
        person.last_name = message.text
        person.save()

        user_dict[chat_id].state.reg_form = 3
        bot.send_message(message.chat.id, 'Вкажіть номер телефону без коду країни( без +38):')

    elif user_dict[chat_id].state.reg_form == 3:
        person = Person.get(telegram_id=sender.id)
        person.phone_number = message.text
        person.save()

        user_dict[chat_id].state.reg_form = 0
        bot.send_message(message.chat.id, 'Дякуємо за те що залишили вашу анкету')
        sender_data = f'Нова анкета додана у базу @{sender.username}, {sender.id}'
        bot.send_message(config.DEVELOPER_ID, sender_data)

    elif user_dict[chat_id].state.send_admin == 1:
        user_dict[chat_id].send.id = message.text
        user_dict[chat_id].state.send_admin = 2
        bot.send_message(message.chat.id, 'Напишіть ваше повідомлення для користувача та натисніть на кнопку '
                                          '"Відправити"')

    elif user_dict[chat_id].state.send_admin == 2:
        bot.send_message(user_dict[chat_id].send.id, message.text)
        user_dict[chat_id].state.send_admin = 0

        bot.send_message(message.chat.id, 'Повідомлення відправлено!')

def get_environment_info():
    from requests import get
    from platform import platform
    ip = get('https://api.ipify.org').text

    return {
        'ip': ip,
        'os': platform()
    }


# RUN
env = get_environment_info()
dev_greet = f'@{me.username} запущен.\nIP: {env["ip"]}\nOS: {env["os"]}'
bot.send_message(config.DEVELOPER_ID, dev_greet)
bot.polling(none_stop=True)
