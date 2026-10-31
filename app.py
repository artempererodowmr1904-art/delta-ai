import os
import telebot
import requests
from flask import Flask, request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
SPACE_URL = "https://jickman125-gemma4-31b-uncensored-assistant.hf.space/api/predict"

dunder_name = "_" * 2 + "name" + "_" * 2
app = Flask(eval(dunder_name))
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 DèltaAI (Gemma 31B) готов. Спрашивай.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    msg = bot.send_message(message.chat.id, "⏳ Думаю (10-20 сек)...")
    
    # Формат, который использует Gradio 4/5 для чатов
    payload = {
        "data": [
            message.text, # текст
            [],           # история (пустая)
            "You are a helpful assistant.", # системный промпт
            1024,         # макс токенов
            0.7,          # температура
        ]
    }
    
    try:
        r = requests.post(SPACE_URL, json=payload, timeout=60)
        if r.status_code == 200:
            res = r.json()
            if "data" in res and len(res["data"]) > 0:
                # Обычно ответ лежит в первом элементе списка
                ai_text = res["data"][0]
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=str(ai_text)[:4000])
            else:
                bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Странный ответ: {res}")
        else:
            bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Ошибка Space: {r.status_code}")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"Ошибка сети: {e}")

@app.route('/', methods=['GET'])
def index():
    return "Bot is alive!", 200

@app.route(f'/{TELEGRAM_TOKEN}', methods=['POST'])
def receive_update():
    if request.headers.get('content-type') == 'application/json':
        update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
        bot.process_new_updates([update])
        return "OK", 200
    return "Bad Request", 403

if eval(dunder_name) == "_" * 2 + "main" + "_" * 2:
    RENDER_URL = "https://delta-ai-tep9.onrender.com" 
    
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
