import os
import telebot
from flask import Flask, request
from gradio_client import Client

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# Твой Space
SPACE_NAME = "jickman125/Gemma4-31b-uncensored-assistant"

dunder_name = "_" * 2 + "name" + "_" * 2
app = Flask(eval(dunder_name))
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "🤖 DèltaAI (Gemma 31B) готов. Спрашивай.")

@bot.message_handler(func=lambda message: True)
def chat(message):
    msg = bot.send_message(message.chat.id, "⏳ Думаю (10-20 сек)...")
    
    try:
        # Подключаемся к Space
        client = Client(SPACE_NAME)
        
        # Отправляем запрос (Gradio обычно принимает текст первым аргументом)
        # Если выдает ошибку, мы попробуем другой формат
        try:
            result = client.predict(message.text, api_name="/chat")
        except:
            result = client.predict(message.text)
            
        ai_text = str(result)
        
        # Чистим ответ от лишних скобок, если Gradio вернул кортеж
        if ai_text.startswith("(") and ai_text.endswith(")"):
            ai_text = ai_text[1:-1]
            
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=ai_text[:4000])
        
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"❌ Ошибка Space: {e}\n\nВозможно, он спит. Зайди на него в браузере и разбуди.")

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
    
    import requests
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
