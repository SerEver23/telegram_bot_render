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

KEYWORDS_TO_IGNORE = [
    "продается", "в наличии", "можно забрать", "за сколько", "цена",
    "стоимость", "купить", "продам", "наличие", "где находится",
    "доставка", "алмере", "ещё есть", "доступен", "можно купить",
    "продаю", "объявление", "торг", "самовывоз", "отдам", "забрать",
    "актуально", "ещё актуально", "есть ли", "осталось", "новый", "б/у", "бушный", "бэушный",
    "продається", "в наявності", "можна забрати", "скільки коштує",
    "ціна", "вартість", "купити", "продам", "наявність", "де знаходиться",
    "доставка", "алмера", "ще є", "доступний", "можна купити",
    "віддам", "оголошення", "є в наявності", "актуально", "самовивіз", "новий", "б/у", "бушне",
    "for sale", "price", "available", "can pick up", "delivery",
    "location", "how much", "still available", "buy", "sell", "selling", "giveaway",
    "отдаю даром", "цена вопроса", "кто заберёт", "можно ли купить", "остался ли", 
    "актуально ли", "кому нужно", "ещё продаётся", "по чём", "по какой цене", 
    "куда забирать", "наличие товара", "ещё можно взять", "продажа"
]

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    text = message.text.lower()

    if "?" not in text:
        return

    if any(keyword in text for keyword in KEYWORDS_TO_IGNORE):
        return

    bot.send_chat_action(message.chat.id, 'typing')

    prompt = f"Ты — эксперт по Нидерландам. Вопрос: {message.text}\nОтвет:"
    try:
        response = model.generate_content(prompt)
        reply = response.text.strip()

        MAX_LIMIT = 300
        HARD_LIMIT = 350

        if len(reply) > MAX_LIMIT:
            cut = reply[:HARD_LIMIT]
            end = max(cut.rfind("."), cut.rfind("!"), cut.rfind("?"))

            if end != -1 and end >= MAX_LIMIT:
                reply = cut[:end + 1].strip()
            else:
                reply = reply[:MAX_LIMIT].strip()
                # Если обрезано без завершения — ставим многоточие
                if not reply.endswith((".", "!", "?")):
                    reply += "..."

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
