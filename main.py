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
RANDOM_DAY_COMMAND_PATTERN = re.compile(r"/\w+ (\d{1,2}\.\d{1,2}(\.\d{4})?)")
TOMORROW_COMMAND_PATTERN = re.compile(r"/\w+ (tomorrow|завтра)")

TZ = pytz.timezone('Europe/Moscow')


@bot.message_handler(commands=['dish'])
def dish(message: telebot.types.Message):
    who(message, 'washes', 'dish')


@bot.message_handler(commands=['cook'])
def cooking(message: telebot.types.Message):
    who(message, 'cooks', 'cooking')


def who(message: telebot.types.Message, action: str, order_key: str):
    if re.match(TOMORROW_COMMAND_PATTERN, message.text):
        day = datetime.datetime.now(TZ) + datetime.timedelta(days=1)
        bot.send_message(message.chat.id, f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} tomorrow.")

    elif (m := re.match(RANDOM_DAY_COMMAND_PATTERN, message.text)) is not None:
        m: re.Match
        if message.text.count('.') == 1:
            message.text += f'.{datetime.datetime.now(TZ).year}'
        try:
            m = re.match(RANDOM_DAY_COMMAND_PATTERN, message.text)
            day = datetime.datetime.strptime(m.group(1), r"%d.%m.%Y").astimezone(TZ)
        except ValueError:
            bot.send_message(message.chat.id, "Invalid date")
        else:
            day += datetime.timedelta(hours=12)
            bot.send_message(message.chat.id, f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} that day.")

    else:
        day = datetime.datetime.now(TZ)
        bot.send_message(message.chat.id, f"{ORDER[order_key][(day - FIRST_DAY).days % 4]} {action} today.")


bot.infinity_polling()
