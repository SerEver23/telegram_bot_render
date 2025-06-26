import os
import telebot
import google.generativeai as genai
from flask import Flask, request
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL")

if not all([TELEGRAM_TOKEN, GEMINI_API_KEY, WEBHOOK_URL]):
    raise ValueError("Не заданы все необходимые переменные окружения.")

# Инициализация Telegram-бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Flask-приложение
app = Flask(__name__)

# Обработка сообщений
@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    text = message.text.strip()

    bot.send_chat_action(message.chat.id, 'typing')

    prompt = (
        f"Ты — эксперт по жизни в Нидерландах и помогаешь людям в групповых чатах.\n"
        f"Пользователь написал сообщение:\n\"{text}\"\n\n"
        f"Если это сообщение содержит общий вопрос, который может быть интересен всем участникам чата — ответь на него кратко и точно.\n"
        f"Если это просто реплика или не требует общего ответа — не отвечай совсем.\n"
        f"Ответь только если ты уверен, что вопрос предназначен для всех.\n"
        f"Если отвечаешь — сделай это кратко, в 1-2 предложения."
    )

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()

        if reply:
            bot.reply_to(message, reply)

    except Exception as e:
        print("Ошибка Gemini:", e)
        bot.reply_to(message, "⚠️ Помилка при зверненні до Gemini API.")

# Webhook endpoint
@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Запуск webhook-сервера
def start_webhook():
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    print(f"Webhook установлен по адресу: {WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    start_webhook()
