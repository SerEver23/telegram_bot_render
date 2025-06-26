import os
import telebot
import google.generativeai as genai
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEBHOOK_URL    = os.getenv("WEBHOOK_URL")

if not all([TELEGRAM_TOKEN, GEMINI_API_KEY, WEBHOOK_URL]):
    raise ValueError("Не заданы все необходимые переменные окружения.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Настройка Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Flask app
app = Flask(__name__)

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    text = message.text.strip()
    lower_text = text.lower()

    # Эвристика: фильтрация рекламы и нерелевантного
    if len(text) > 700:
        return
    if sum(text.count(e) for e in "🌞🌲🏡🍽🎨👫👩‍🏫✅❌📌📞") >= 4:
        return
    if not any(lower_text.startswith(q) for q in ["как", "что", "почему", "зачем", "где", "можно ли", "кто", "есть ли"]) and "?" not in lower_text:
        return

    bot.send_chat_action(message.chat.id, 'typing')

    prompt = (
        f"Ты — эксперт по жизни в Нидерландах и помогаешь людям в групповых чатах.\n"
        f"Вот сообщение:\n\"{text}\"\n\n"
        f"Если это обычное объявление, реклама, событие или информация, не содержащая общего вопроса — не отвечай.\n"
        f"Если это общий вопрос, интересный всем участникам — ответь кратко (1–2 предложения).\n"
        f"Если не уверен, лучше промолчи."
    )

    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()

        if reply:
            bot.reply_to(message, reply)

    except Exception as e:
        print("Ошибка Gemini:", e)
        bot.reply_to(message, "⚠️ Помилка при зверненні до Gemini API.")

def start_webhook():
    bot.remove_webhook()
    bot.set_webhook(f"{WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    print(f"Webhook установлен по адресу: {WEBHOOK_URL}/{TELEGRAM_TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

if __name__ == "__main__":
    start_webhook()
