import os
import telebot
import requests
import json
from flask import Flask, request

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Ссылки на твои Space
SPACES = [
    "https://lejobuildyt-qwen3-6-35b-a3b-uncensored-hauhaucs-aggressive-gguf-q6-k-p.hf.space/api/predict",
    "https://jickman125-gemma4-31b-uncensored-assistant.hf.space/api/predict"
]

dunder_name = "_" * 2 + "name" + "_" * 2
app = Flask(eval(dunder_name))
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 DèltaAI готов. Спрашивай (модель 35B без цензуры).")

@bot.message_handler(func=lambda message: True)
def chat(message):
    msg = bot.send_message(message.chat.id, "⏳ Думаю (это может занять 10-20 сек)...")
    
    ai_text = None
    for space_url in SPACES:
        try:
            # Формат запроса Gradio (может отличаться в разных версиях)
            # Пробуем разные варианты
            payloads = [
                {"data": [message.text]},
                {"data": [[message.text, None]]},
                {"data": [message.text, 0.7, 1024]}
            ]
            
            for payload in payloads:
                r = requests.post(space_url, json=payload, timeout=60)
                if r.status_code == 200:
                    res = r.json()
                    if "data" in res and len(res["data"]) > 0:
                        ai_text = str(res["data"][0])
                        break
            
            if ai_text: break
        except Exception as e:
            print(f"Ошибка {space_url}: {e}")
            continue
            
    if not ai_text:
        ai_text = "❌ Все Space спят или не отвечают. Попробуй позже или разбуди их на сайте Hugging Face."
        
    bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=ai_text[:4000])

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
