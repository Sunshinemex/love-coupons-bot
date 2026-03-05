import telebot
import json
import random
from datetime import datetime

TOKEN = "8712590812:AAFrsZYzeKmhN3DzbolNlzU16ixNUnRAgf0"
OWNER_ID = 200869072

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

love_replies = [
"Этот бот сделан с любовью для тебя 💌",
"Мне нравится радовать тебя ❤️"
]

messages = [
"🐀 Я тебя люблю, потому что у тебя стильная прическа!",
"🐀 Я тебя люблю, потому что ты мой самый классный бизнесмен!",
"🐀 Я горжусь тобой больше, чем ты думаешь 🤍",
"🐀 Я тебя люблю, потому что ты самый заботливый!",
"🐀 Ты — мой личный герой без плаща",
"🐀 Даже в плохой день ты — моё хорошее",
"🐀 Люблю тебя так сильно, что даже вселенная немного завидует"
]

coupons = [
"🧡 Купон на массаж",
"🧡 Купон на массаж",
"🧡 Купон на массаж ног",
"🧡 Купон на кофе в постель",
"🧡 Купон на поцелуй",
"🧡 Купон на выгул Тузика утром",
"🩵 Купон на свидание",
"🩵 Купон на желание",
"🩵 Ужин на твой выбор",
"🩵 Купон «Поцелуйная атака»",
"❤️ Купон «Я официально признаю, что ты был прав»",
"❤️ Купон «Ночь компьютерного рейда»",
"❤️‍🔥 Купон «Не дурю голову целый день»",
"❤️‍🔥 Купон на исполнение любой тайной фантазии",
"❤️‍🔥 Купон «Доброе утро по-особенному»",
"❤️‍🔥 Купон «День услужливой жены»"
]


def load():
    try:
        with open(DATA_FILE) as f:
            return json.load(f)
    except:
        data = {
            "last_day":"",
            "message_opened":False,
            "opened_today":0,
            "activated_today":0,
            "coupons":[{"name":c,"opened":False,"used":False} for c in coupons]
        }
        save(data)
        return data


def save(data):
    with open(DATA_FILE,"w") as f:
        json.dump(data,f)


def reset(data):
    today=str(datetime.now().date())
    if data["last_day"]!=today:
        data["last_day"]=today
        data["message_opened"]=False
        data["opened_today"]=0
        data["activated_today"]=0


def love_message(chat):
    if random.randint(1,3)==1:
        bot.send_message(chat, random.choice(love_replies))


@bot.message_handler(commands=["start"])
def start(m):

    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💌 Послание дня")
    kb.add("🎁 Мои купоны")

    bot.send_message(
        m.chat.id,
        "Привет, любимый муж! 💕\n\nОткрой своё послание дня\nи не забудь про купоны! 💌🎁",
        reply_markup=kb
    )


@bot.message_handler(func=lambda m: m.text=="💌 Послание дня")
def message_day(m):

    data=load()
    reset(data)

    if data["message_opened"]:
        bot.send_message(m.chat.id,"💌 Сегодняшнее послание уже открыто.\n\nВозвращайся завтра ❤️")
        return

    text=random.choice(messages)

    data["message_opened"]=True
    save(data)

    bot.send_message(m.chat.id,f"💌 Послание дня\n\n{text}")

    love_message(m.chat.id)


@bot.message_handler(func=lambda m: m.text=="🎁 Мои купоны")
def coupons_menu(m):

    data=load()
    reset(data)

    kb=telebot.types.InlineKeyboardMarkup()

    for i,c in enumerate(data["coupons"]):

        if not c["opened"]:
            t="🎁 Открой меня"
        elif c["used"]:
            t=c["name"]+" ✅"
        else:
            t=c["name"]

        kb.add(
            telebot.types.InlineKeyboardButton(
                t,
                callback_data=f"open_{i}"
            )
        )

    bot.send_message(
        m.chat.id,
        f"🎁 Твои купоны\n\nСегодня можно открыть: {2-data['opened_today']}\nАктивировать: {1-data['activated_today']}",
        reply_markup=kb
    )


@bot.callback_query_handler(func=lambda call:True)
def click(call):

    data=load()
    reset(data)

    if call.data.startswith("open_"):

        i=int(call.data.split("_")[1])
        c=data["coupons"][i]

        if not c["opened"]:

            if data["opened_today"]>=2:
                bot.answer_callback_query(call.id,"Сегодня можно открыть только 2 купона")
                return

            c["opened"]=True
            data["opened_today"]+=1
            save(data)

            kb=telebot.types.InlineKeyboardMarkup()

            kb.add(
                telebot.types.InlineKeyboardButton(
                    "Активировать купон",
                    callback_data=f"use_{i}"
                )
            )

            kb.add(
                telebot.types.InlineKeyboardButton(
                    "Назад",
                    callback_data="back"
                )
            )

            bot.send_message(
                call.message.chat.id,
                f"🎉 Сюрприз!\n\n{c['name']}",
                reply_markup=kb
            )

            love_message(call.message.chat.id)

        else:

            bot.answer_callback_query(call.id,"Купон уже открыт")



    elif call.data.startswith("use_"):

        i=int(call.data.split("_")[1])
        c=data["coupons"][i]

        if c["used"]:
            bot.answer_callback_query(call.id,"Уже использован")
            return

        if data["activated_today"]>=1:
            bot.answer_callback_query(call.id,"Можно активировать только 1 купон в день")
            return

        c["used"]=True
        data["activated_today"]+=1
        save(data)

        bot.send_message(
            call.message.chat.id,
            f"🎟 Купон активирован!\n\n{c['name']}"
        )

        bot.send_message(
            OWNER_ID,
            f"❤️ Муж активировал купон:\n\n{c['name']}"
        )

        love_message(call.message.chat.id)


    elif call.data=="back":

        coupons_menu(call.message)


bot.infinity_polling()
