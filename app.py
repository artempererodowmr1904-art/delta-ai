import os
import telebot
from flask import Flask, request
from gradio_client import Client

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

# ССЫЛКИ НА ТВОИ SPACE
SPACES = [
    "LejobuildYT/Qwen3.6-35B-A3B-Uncensored-HauhauCS-Aggressive_GGUF-Q6_K_P",
    "jickman125/Gemma4-31b-uncensored-assistant"
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
    for space in SPACES:
        try:
            # Подключаемся к Space
            client = Client(space)
            # Отправляем запрос (интерфейс Gradio обычно принимает текст как первый аргумент)
            result = client.predict(message.text, api_name="/predict")
            
            # Gradio возвращает либо строку, либо словарь
            if isinstance(result, str):
                ai_text = result
            elif isinstance(result, dict) and "response" in result:
                ai_text = result["response"]
            else:
                ai_text = str(result)
                
            if ai_text: break # Если получили ответ, выходим из цикла
        except Exception as e:
            print(f"Ошибка Space {space}: {e}")
            continue
            
    if not ai_text:
        ai_text = "❌ Не удалось получить ответ ни от одного Space. Возможно, они спят или перегружены."
        
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
    
    import requests
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook")
    webhook_url = f"{RENDER_URL}/{TELEGRAM_TOKEN}"
    requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={webhook_url}")

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
