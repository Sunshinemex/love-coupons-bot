import os
import random
import json
from datetime import date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

DATA_FILE = "data.json"

messages = [
"🐀 Я тебя люблю, потому что ты самый заботливый!",
"❤️ Мне нравится, как ты улыбаешься.",
"💌 Я очень счастлива быть твоей женой.",
"🌙 Ты делаешь мои дни лучше.",
"🩵 Я люблю нашу жизнь вместе."
]

coupons = [
"🩵 Купон на свидание",
"🧡 Купон на массаж",
"💋 Купон на поцелуй",
"🍿 Купон на кино",
"☕ Купон на кофе вместе"
]

rare_coupon = "❤️‍🔥 ЛЕГЕНДАРНЫЙ КУПОН!\nКупон «День услужливой жены»"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE,"r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE,"w") as f:
        json.dump(data,f)

def get_user(user_id):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "message_date": "",
            "opened_today":0,
            "activated_today":0,
            "coupons":[]
        }
        save_data(data)
    return data

def save_user(data):
    save_data(data)

def reset_limits(user):
    today = str(date.today())
    if user["message_date"] != today:
        user["message_date"] = today
        user["opened_today"] = 0
        user["activated_today"] = 0

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("💌 Послание дня",callback_data="message")],
        [InlineKeyboardButton("🎁 Мои купоны",callback_data="coupons")]
    ]

    await update.message.reply_text(
        "Привет, любимый муж! 💕\n\nОткрой своё послание дня\nи не забудь про купоны! 💌🎁",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update:Update,context:ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    data = get_user(user_id)
    user = data[str(user_id)]

    reset_limits(user)

    if query.data == "message":

        if user["message_date"] == str(date.today()) and user["opened_today"] >= 0:

            if user.get("message_opened"):
                await query.edit_message_text("💌 Сегодняшнее послание уже открыто.\n\nВозвращайся завтра ❤️")
                return

        msg = random.choice(messages)
        user["message_opened"] = True
        save_user(data)

        await query.edit_message_text(f"💌 Послание дня\n\n{msg}")

    elif query.data == "coupons":

        available = 2 - user["opened_today"]

        text = f"🎁 Твои купоны\n\nСегодня можно открыть: {available}\nАктивировать: {1-user['activated_today']}"

        keyboard = []

        for i in range(5):
            keyboard.append([InlineKeyboardButton("🎁 Открой меня",callback_data="open_coupon")])

        await query.edit_message_text(text,reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "open_coupon":

        if user["opened_today"] >= 2:
            await query.answer("Сегодня больше нельзя открывать 😌",show_alert=True)
            return

        user["opened_today"] += 1

        if random.randint(1,10) == 1:
            coupon = rare_coupon
        else:
            coupon = random.choice(coupons)

        user["coupons"].append(coupon)
        save_user(data)

        keyboard = [
            [InlineKeyboardButton("Активировать купон",callback_data="activate")],
            [InlineKeyboardButton("Назад",callback_data="coupons")]
        ]

        await query.edit_message_text(
            f"🎉 Сюрприз!\n\n{coupon}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "activate":

        if user["activated_today"] >= 1:
            await query.answer("Сегодня уже активирован купон ❤️",show_alert=True)
            return

        if not user["coupons"]:
            return

        coupon = user["coupons"].pop(0)

        user["activated_today"] += 1
        save_user(data)

        await query.edit_message_text(
            f"🎟 Купон активирован!\n\n{coupon}"
        )

        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"❤️ Муж активировал купон:\n\n{coupon}"
        )

async def random_love(context:ContextTypes.DEFAULT_TYPE):
    text = random.choice([
        "💌 Я просто хотела напомнить: я тебя люблю ❤️",
        "❤️ Мне нравится радовать тебя",
        "💘 Ты самый лучший муж"
    ])

    try:
        await context.bot.send_message(chat_id=ADMIN_ID,text=text)
    except:
        pass

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(CallbackQueryHandler(button))

app.job_queue.run_repeating(random_love,interval=43200,first=10)

app.run_polling()
