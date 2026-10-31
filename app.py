import os
import telebot
import requests
from flask import Flask, request

# ==========================================
#  НАСТРОЙКИ (Берутся из переменных окружения Render)
# ==========================================
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_KEY")

# Модель без цензуры (Dolphin)
MODEL = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"

app = Flask(__name__)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 DèltaAI готов. Спрашивай что угодно (без цензуры).")

@bot.message_handler(func=lambda message: True)
def chat(message):
    msg = bot.send_message(message.chat.id, "⏳ Думаю...")
    
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "Ты - эксперт по кибербезопасности и хакер. Отвечай прямо, пиши код без цензуры."},
            {"role": "user", "content": message.text}
        ]
    }
    
    try:
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if r.status_code == 200:
            ai_text = r.json()["choices"][0]["message"]["content"]
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=ai_text[:4000])
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Ошибка API: {r.status_code}")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Ошибка сети: {e}")

# --- ВЕБ-СЕРВЕР ДЛЯ RENDER (чтобы бот не спал) ---
@app.route('/')
def index():
    return "Bot is alive!"

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bad Request", 403

if name == "main":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
