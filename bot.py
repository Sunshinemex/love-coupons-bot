import json
import random
from datetime import date
from aiogram import Bot, Dispatcher, executor, types

TOKEN = "8712590812:AAFrsZYzeKmhN3DzbolNlzU16ixNUnRAgf0"
WIFE_ID = 200869072

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

today = str(date.today())

messages = [
"🐀 Я тебя люблю, потому что у тебя стильная прическа!",
"🐀 Я тебя люблю, потому что ты мой самый классный бизнесмен!",
"🐀 Я тебя люблю, потому что ты самый заботливый!",
"🐀 Я тебя люблю, потому что ты красавчик!",
"🐀 Я тебя люблю, потому что ты самый смешной!",
"🐀 Я тебя люблю сильнее, чем ты любишь побеждать в доте 😏",
"🐀 Ты мой самый любимый человек на всей планете.",
"🐀 Даже в плохой день ты — моё хорошее.",
"🐀 Люблю тебя так сильно, что даже вселенная немного завидует."
]

coupons = [
"🧡 Купон на массаж",
"🧡 Купон на массаж",
"🧡 Купон на массаж ног",
"🧡 Купон на поцелуй",
"🧡 Купон на кофе в постель",
"🧡 Купон на Макдональдс",
"🩵 Купон на свидание",
"🩵 Купон на желание",
"🩵 Ужин на твой выбор",
"❤️ Купон «Я официально признаю, что ты был прав»",
"❤️‍🔥 Купон «День услужливой жены»"
]

def load_data():
    with open("coupons.json") as f:
        return json.load(f)

def save_data(data):
    with open("coupons.json","w") as f:
        json.dump(data,f)

def main_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💌 Послание дня")
    kb.add("🎁 Мои купоны")
    return kb

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    text = (
        "Привет, любимый муж! 💕\n\n"
        "Открой своё послание дня\n"
        "и не забудь про купоны! 💌🎁"
    )
    await msg.answer(text, reply_markup=main_menu())

@dp.message_handler(lambda m: m.text=="💌 Послание дня")
async def message_day(msg: types.Message):
    data = load_data()

    if data.get("message_day")==today:
        await msg.answer("💌 Сегодняшнее послание уже открыто.\n\nВозвращайся завтра ❤️")
        return

    message=random.choice(messages)
    data["message_day"]=today
    save_data(data)

    await msg.answer(f"💌 Послание дня:\n\n{message}")

@dp.message_handler(lambda m: m.text=="🎁 Мои купоны")
async def coupons_menu(msg: types.Message):
    data=load_data()

    kb=types.InlineKeyboardMarkup()

    for i in range(5):
        kb.add(types.InlineKeyboardButton("🎁 Открой меня",callback_data=f"open_{i}"))

    await msg.answer(
        "🎁 Твои купоны\n\n"
        "Сегодня можно открыть: 2\n"
        "Активировать: 1",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data.startswith("open"))
async def open_coupon(call: types.CallbackQuery):

    coupon=random.choice(coupons)

    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("Активировать купон",callback_data=f"activate_{coupon}"))

    await call.message.answer(
        f"🎉 Сюрприз!\n\n{coupon}",
        reply_markup=kb
    )

@dp.callback_query_handler(lambda c: c.data.startswith("activate"))
async def activate_coupon(call: types.CallbackQuery):

    coupon=call.data.replace("activate_","")

    await call.message.answer(
        f"🎟 Купон активирован!\n\n{coupon}"
    )

    await bot.send_message(
        WIFE_ID,
        f"❤️ Муж активировал купон:\n\n{coupon}"
    )

if __name__=="__main__":
    executor.start_polling(dp)
