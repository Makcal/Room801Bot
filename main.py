#!python3.11
import os
import datetime
import re
import pytz

import telebot


BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

FIRST_DAY = datetime.datetime.fromisoformat("2023-09-13T08:00+03:00")
ORDER = {
    'dish':    ["Макс", "Саня", "Лев", "Даниел"],
    'cooking': ["Даниел", "Лев", "Саня", "Макс"],
}

STOVE_WASH_WEEKDAYS = [1, 5]

RANDOM_DAY_COMMAND_PATTERN = re.compile(r"/\w+ (\d{1,2}\.\d{1,2}(\.\d{4})?)")
TOMORROW_COMMAND_PATTERN = re.compile(r"/\w+ (tomorrow|завтра)")

TIME_ZONE = pytz.timezone('Europe/Moscow')


@bot.message_handler(commands=['dish'])
def dish(message: telebot.types.Message):
    who(message, 'washes', 'dish')


@bot.message_handler(commands=['cook'])
def cooking(message: telebot.types.Message):
    who(message, 'cooks', 'cooking')


def who(message: telebot.types.Message, action: str, order_key: str):
    if re.match(TOMORROW_COMMAND_PATTERN, message.text):
        day = datetime.datetime.now(TIME_ZONE) + datetime.timedelta(days=1)
        message_to_send = f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} tomorrow."
        if day.weekday() in STOVE_WASH_WEEKDAYS:
            message_to_send += "And also he has to wash the stove"
        bot.reply_to(message, message_to_send)

    elif (m := re.match(RANDOM_DAY_COMMAND_PATTERN, message.text)) is not None:
        m: re.Match
        if message.text.count('.') == 1:
            message.text += f'.{datetime.datetime.now(TIME_ZONE).year}'
        try:
            m = re.match(RANDOM_DAY_COMMAND_PATTERN, message.text)
            day = datetime.datetime.strptime(m.group(1), r"%d.%m.%Y").astimezone(TIME_ZONE)
        except ValueError:
            bot.reply_to(message, "Invalid date")
        else:
            day += datetime.timedelta(hours=12)
            bot.reply_to(message, f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} that day.")

    else:
        day = datetime.datetime.now(TIME_ZONE)
        bot.reply_to(message, f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} today.")


bot.infinity_polling()
