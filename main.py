import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv
import google.generativeai as genai

# Загрузка переменных окружения из .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

# Инициализация Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Flask приложение
app = Flask(__name__)

# Обработка входящих сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    prompt = f"Ты — эксперт по Нидерландам. Вопрос: {message.text}\nОтвет:"
    try:
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text.strip())
    except Exception as e:
        print("Ошибка Gemini:", e)
        bot.reply_to(message, "⚠️ Ошибка при обращении к Gemini API.")

# Webhook обработка
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Главная страница (health check)
@app.route("/", methods=["GET"])
def index():
    return "Бот работает!"

# Установка Webhook при запуске
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=8080)
