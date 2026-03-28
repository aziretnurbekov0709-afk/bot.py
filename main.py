import telebot
from telebot import types
import requests
import time
import threading

BOT_TOKEN = "8656129697:AAH4g6qI-7aRKH7yYEA_1j_CHUJKHhmb5PI"
CRYPTO_TOKEN = "UQD4kfKvot7S7a-k0D7YLsRQquU5pOQ6Lj7vjNh9uzn7Q-ep"
ADMIN_ID = 6498779131

bot = telebot.TeleBot(BOT_TOKEN)

# 📌 Меню
def main_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("📂 Мои работы", callback_data="works"))
    kb.add(types.InlineKeyboardButton("💼 Услуги", callback_data="services"))
    kb.add(types.InlineKeyboardButton("💰 Цены", callback_data="prices"))
    kb.add(types.InlineKeyboardButton("📩 Заказать", callback_data="order"))
    kb.add(types.InlineKeyboardButton("📝 Оставить отзыв", callback_data="review"))
    return kb

# ▶️ Старт
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        "👋 Привет!\n\nЯ создаю:\n🌐 Сайты\n🤖 Telegram-ботов\n📊 Презентации\n\nВыбери ниже 👇",
        reply_markup=main_menu()
    )

# 🔘 Кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == "works":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🌐 Сайт", url="https://sites.google.com/view/meruryielts9/%D0%B3%D0%BB%D0%B0%D0%B2%D0%BD%D0%B0%D1%8F-%D1%81%D1%82%D1%80%D0%B0%D0%BD%D0%B8%D1%86%D0%B0"))
        kb.add(types.InlineKeyboardButton("🤖 Бот", url="https://t.me@fahdesign_bot"))
        bot.send_message(call.message.chat.id, "📂 Мои работы 👇", reply_markup=kb)

    elif call.data == "services":
        bot.send_message(call.message.chat.id,
            "💼 Услуги:\n🌐 Сайты\n🤖 Боты\n📊 Презентации")

    elif call.data == "prices":
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💰 Купить сайт (50$)", callback_data="buy_site"))
        kb.add(types.InlineKeyboardButton("🤖 Купить бот (1000 сом)", callback_data="buy_bot"))
        bot.send_message(call.message.chat.id, "💰 Выбери 👇", reply_markup=kb)

    elif call.data == "buy_site":
        create_payment(call.message.chat.id, "50", "Сайт")

    elif call.data == "buy_bot":
        create_payment(call.message.chat.id, "12.7", "Бот")

    elif call.data == "order":
        bot.send_message(call.message.chat.id, "📩 Напиши заказ")

    elif call.data == "review":
        msg = bot.send_message(call.message.chat.id, "📝 Напишите отзыв:")
        bot.register_next_step_handler(msg, save_review)

# 💰 Платеж
def create_payment(chat_id, amount, service):
    url = "https://pay.crypt.bot/api/createInvoice"
    headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
    data = {"asset": "USDT", "amount": amount}

    r = requests.post(url, json=data, headers=headers).json()
    pay_url = r["result"]["pay_url"]
    invoice_id = r["result"]["invoice_id"]

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💳 Оплатить", url=pay_url))

    bot.send_message(chat_id, "Оплати 👇", reply_markup=kb)

    threading.Thread(target=check_payment, args=(chat_id, invoice_id, service, amount)).start()

# 🔁 Проверка оплаты
def check_payment(chat_id, invoice_id, service, amount):
    while True:
        time.sleep(10)
        url = f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}"
        headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}

        r = requests.get(url, headers=headers).json()
        status = r["result"]["items"][0]["status"]

        if status == "paid":
            bot.send_message(chat_id, f"✅ Оплата получена: {service}")
            bot.send_message(ADMIN_ID, f"💰 Новый заказ\n{service} — {amount}")
            break

# 📝 Отзыв
def save_review(msg):
    bot.send_message(ADMIN_ID, f"📝 Отзыв:\n{msg.text}")
    bot.send_message(msg.chat.id, "🙏 Спасибо!")

# 🤖 Автоответ
@bot.message_handler(func=lambda m: True)
def auto_reply(msg):
    text = msg.text.lower()

    if "сайт" in text:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💳 Купить", callback_data="buy_site"))
        bot.send_message(msg.chat.id, "Сайт 50$", reply_markup=kb)

    elif "бот" in text:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("💳 Купить", callback_data="buy_bot"))
        bot.send_message(msg.chat.id, "Бот 1000 сом", reply_markup=kb)

    else:
        bot.send_message(msg.chat.id, "Выбери 👇", reply_markup=main_menu())

# ▶️ Запуск
bot.infinity_polling()
