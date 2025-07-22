import os
import telebot
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

if not all([TELEGRAM_TOKEN, WEBHOOK_URL, SPOONACULAR_API_KEY]):
    raise ValueError("Не заданы все необходимые переменные окружения.")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
app = Flask(__name__)

MUST_ANSWER_KEYWORDS = [
    "скажите", "ищу", "как", "кто знает", "кто занимается", "подскажите", "кто может", "знает", "посоветуйте", "кто", "помогите", "сто",
    "скажіть", "шукаю", "як", "хто знає", "хто займається", "підкажіть", "підказати", "хто може", "знає", "Порадьте", "хто", "допоможіть", "сто",
    "tell me", "looking for", "how", "who knows", "who does", "who handles", "can you tell me", "who can", "knows", "Please advise", "who", "help", "service station"
]

@app.route(f"/{TELEGRAM_TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@bot.message_handler(commands=['recipe', 'рецепт'])
def send_recipe(message):
    query = message.text.replace('/recipe', '').replace('/рецепт', '').strip()
    if not query:
        bot.reply_to(message, "🍽 Введите запрос, например: `/recipe pasta`")
        return

    url = f"https://api.spoonacular.com/recipes/complexSearch"
    params = {
        "query": query,
        "number": 1,
        "apiKey": SPOONACULAR_API_KEY
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()

        if data.get("results"):
            recipe = data["results"][0]
            title = recipe["title"]
            link = f"https://spoonacular.com/recipes/{title.replace(' ', '-')}-{recipe['id']}"
            bot.reply_to(message, f"🥗 {title}\n🔗 {link}")
        else:
            bot.reply_to(message, "🙁 Рецепты не найдены.")
    except Exception as e:
        print("Ошибка Spoonacular:", e)
        bot.reply_to(message, "⚠️ Ошибка при поиске рецепта.")

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_message(message):
    text = message.text.strip()
    lower_text = text.lower()

    must_answer = any(keyword in lower_text for keyword in MUST_ANSWER_KEYWORDS)

    if not must_answer:
        if len(text) > 700:
            return
        if sum(text.count(e) for e in "🌞🌲🏡🍽🎨👫👩‍🏫✅❌📌📞") >= 4:
            return
        if not any(lower_text.startswith(q) for q in ["как", "что", "почему", "зачем", "где", "можно ли", "кто", "есть ли", "who", "how", "where", "can"]) and "?" not in lower_text:
            return

    bot.send_chat_action(message.chat.id, 'typing')

    try:
        # Можно подключить ИИ или ответ по шаблону здесь
        bot.reply_to(message, "🤖 Напишите `/recipe борщ`, чтобы получить рецепт.")
    except Exception as e:
        print("Ошибка обработки сообщения:", e)

def start_webhook():
    bot.remove_webhook()
    webhook_url = f""{https://telegram-recipe-bot-o1dc.onrender.com}/{7876262231:AAH1J7Tci9CrI5IizkrT8PUvnMI74jJ3Vzo}""
    bot.set_webhook(webhook_url)
    print(f"Webhook установлен по адресу: {webhook_url}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    start_webhook()
