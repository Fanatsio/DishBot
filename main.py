import asyncio
import json
import os
import logging
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN", "")
DATA_FILE = "data.json"

logging.basicConfig(level=logging.INFO)

if not TOKEN:
    raise ValueError("❌ BOT_TOKEN не найден в .env файле!")

class Storage:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = {"users": [], "history": []}
        self.load()

    def load(self):
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.save()

    def save(self):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_user(self, user_id: int, name: str) -> bool:
        if not any(u["id"] == user_id for u in self.data["users"]):
            self.data["users"].append({"id": user_id, "name": name})
            self.save()
            return True
        return False

    def add_history(self, name: str) -> bool:
        today = str(date.today())

        if any(h["date"] == today and h["user"] == name for h in self.data["history"]):
            return False

        self.data["history"].append({"date": today, "user": name})
        self.save()
        return True

    def get_history(self, limit: int = 10) -> str:
        if not self.data["history"]:
            return "История пока пуста."

        text = "🕑 История мытья:\n"
        for h in self.data["history"][-limit:]:
            text += f"{h['date']}: {h['user']}\n"
        return text

storage = Storage(DATA_FILE)
bot = Bot(TOKEN)
dp = Dispatcher()

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="✅ Я помыл")],
        [KeyboardButton(text="🕑 История")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    uid = message.from_user.id
    name = message.from_user.full_name
    if storage.add_user(uid, name):
        await message.answer(f"Ты добавлен в список, {name}!", reply_markup=main_kb)
    else:
        await message.answer("Ты уже есть в списке.", reply_markup=main_kb)

@dp.message(lambda msg: msg.text == "✅ Я помыл")
async def cmd_done(message: types.Message):
    name = message.from_user.full_name
    if storage.add_history(name):
        await message.answer(f"✅ Отлично! {name} помыл(а) посуду.")
    else:
        await message.answer("Ты уже отмечался сегодня 😉")

@dp.message(lambda msg: msg.text == "🕑 История")
async def cmd_history(message: types.Message):
    await message.answer(storage.get_history())

async def main():
    logging.info("🚀 Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
