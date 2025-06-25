import telebot
import os
from flask import Flask, request

TOKEN = os.environ.get("TELEGRAM_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Обработчик команд
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я работаю через Webhook 🚀")

# Обработка POST-запросов от Telegram
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    bot.process_new_messages([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "", 200

# Главная страница (для проверки работоспособности)
@app.route("/", methods=["GET"])
def index():
    return "Бот работает через Webhook!", 200

# Установка Webhook
if __name__ == "__main__":
    # Установить Webhook на внешний URL
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL") + "/" + TOKEN
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    app.run(host="0.0.0.0", port=8080)
