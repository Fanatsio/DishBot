import asyncio
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import date
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
DATA_FILE = "data.json"

# Загружаем или инициализируем данные
try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"users": [], "history": []}

bot = Bot(TOKEN)
dp = Dispatcher()


def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# --- КНОПКИ ---
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
    if uid not in [u["id"] for u in data["users"]]:
        data["users"].append({"id": uid, "name": name})
        save_data()
        await message.answer(f"Ты добавлен в список, {name}!", reply_markup=main_kb)
    else:
        await message.answer("Ты уже есть в списке.", reply_markup=main_kb)


@dp.message(lambda msg: msg.text == "✅ Я помыл")
async def cmd_done(message: types.Message):
    name = message.from_user.full_name

    # Записываем в историю
    data["history"].append({
        "date": str(date.today()),
        "user": name
    })
    save_data()

    await message.answer(f"✅ Отлично! {name} помыл(а) посуду.")


@dp.message(lambda msg: msg.text == "🕑 История")
async def cmd_history(message: types.Message):
    if not data["history"]:
        await message.answer("История пока пуста.")
        return
    text = "История мытья:\n"
    for h in data["history"][-10:]:
        text += f"{h['date']}: {h['user']}\n"
    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
