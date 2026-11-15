import asyncio
import logging
import os

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message

# ====== НАСТРОЙКИ ======
TG_TOKEN = "9267949771:AAEW6SZ-G_rroNkB2l5GDGlILDO6W63ZQM8"
VENICE_KEY = "VENICE_INFERENCE_KEY_4bvaY_8R9NHhs01hvrrSSRU79HpPwC_GfKFEW1cZ0I"
VENICE_URL = "https://api.venice.ai/api/v1/chat/completions"
MODEL = "venice-uncensored"   # можно заменить: llama-3.3-70b, qwen3-235b-a22b-instruct-2507 и др.
MAX_HISTORY = 20
# =======================

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

history: dict[int, list[dict]] = {}


async def ask_venice(messages: list[dict]) -> str:
    headers = {
        "Authorization": f"Bearer {VENICE_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
    }
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            r = await client.post(VENICE_URL, headers=headers, json=payload)
            if r.status_code != 200:
                return f"⚠️ Ошибка API {r.status_code}:\n{r.text[:500]}"
            data = r.json()
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ Ошибка запроса: {type(e).__name__}: {e}"


@dp.message(Command("start"))
async def cmd_start(message: Message):
    history.pop(message.from_user.id, None)
    await message.answer(
        "👋 Привет! Я бот на Venice AI.\n"
        "Просто напиши сообщение — я отвечу.\n\n"
        "/reset — очистить историю диалога."
    )


@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    history.pop(message.from_user.id, None)
    await message.answer("🧹 История очищена.")


@dp.message(F.text)
async def on_text(message: Message):
    user_id = message.from_user.id
    text = message.text.strip()
    if not text:
        return

    await bot.send_chat_action(message.chat.id, "typing")

    msgs = history.setdefault(user_id, [])
    msgs.append({"role": "user", "content": text})
    if len(msgs) > MAX_HISTORY:
        history[user_id] = msgs[-MAX_HISTORY:]
        msgs = history[user_id]

    answer = await ask_venice(msgs)
    msgs.append({"role": "assistant", "content": answer})

    for i in range(0, len(answer), 4000):
        await message.answer(answer[i:i + 4000])


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
