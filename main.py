import telebot
import os
from keep_alive import keep_alive

bot = telebot.TeleBot(os.environ.get("TELEGRAM_TOKEN"))

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен!")

keep_alive()
bot.polling()
