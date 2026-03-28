import asyncio
from aiogram import Bot, Dispatcher, types
import aiohttp

# ⚙ Настройки
BOT_TOKEN = "8656129697:AAFzWfjA7YBsJoV3rdr99pWrBmpYFjbAIUM"  # токен от BotFather
CRYPTO_TOKEN = "UQD4kfKvot7S7a-k0D7YLsRQquU5pOQ6Lj7vjNh9uzn7Q-ep"  # CryptoBot API
ADMIN_ID = 6498779131  # твой Telegram ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# 📌 Главное меню
def main_menu():
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📂 Мои работы", callback_data="works")],
        [types.InlineKeyboardButton(text="💼 Услуги", callback_data="services")],
        [types.InlineKeyboardButton(text="💰 Цены", callback_data="prices")],
        [types.InlineKeyboardButton(text="📩 Заказать", callback_data="order")],
        [types.InlineKeyboardButton(text="📝 Оставить отзыв", callback_data="review")]
    ])

# ▶️ Старт
@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer(
        "👋 Привет!\n\nЯ создаю:\n🌐 Сайты\n🤖 Telegram-ботов\n📊 Презентации\n\nВыбери ниже 👇",
        reply_markup=main_menu()
    )

# 📂 Мои работы
@dp.callback_query_handler(lambda c: c.data == "works")
async def works(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🌐 Сайт (Skazka Centre)", url="https://sites.google.com/view/skazka-centre-orig/главная-страница")],
        [types.InlineKeyboardButton(text="🤖 Telegram бот", url="https://t.me/fahdesign_bot")]
    ])
    await callback.message.answer("📂 Мои работы 👇", reply_markup=kb)

# 💼 Услуги
@dp.callback_query_handler(lambda c: c.data == "services")
async def services(callback: types.CallbackQuery):
    await callback.message.answer(
        "💼 Услуги:\n\n"
        "🌐 Создание сайтов\n"
        "🤖 Telegram боты\n"
        "📊 Презентации"
    )

# 💰 Цены
@dp.callback_query_handler(lambda c: c.data == "prices")
async def prices(callback: types.CallbackQuery):
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💰 Купить сайт (50$)", callback_data="buy_site")],
        [types.InlineKeyboardButton(text="🤖 Купить Telegram бот (1000 сом)", callback_data="buy_bot")]
    ])
    await callback.message.answer(
        "💰 Цены:\n\n"
        "🌐 Сайт — 50$\n"
        "🤖 Telegram бот — 1000 сом (~$12,7)\n\nВыбери 👇",
        reply_markup=kb
    )

# 📩 Заказ
@dp.callback_query_handler(lambda c: c.data == "order")
async def order(callback: types.CallbackQuery):
    await callback.message.answer("📩 Напиши сюда свой заказ и я свяжусь с тобой!")

# 📝 Оставить отзыв
@dp.callback_query_handler(lambda c: c.data == "review")
async def review(callback: types.CallbackQuery):
    await callback.message.answer("📝 Пожалуйста, напишите свой отзыв. Я сохраню его и отправлю мне.")

# 🔥 Создание счёта через CryptoBot API
async def create_invoice(amount, currency="USDT"):
    async with aiohttp.ClientSession() as session:
        headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
        data = {"asset": currency, "amount": amount}
        async with session.post(
            "https://pay.crypt.bot/api/createInvoice",
            json=data,
            headers=headers
        ) as resp:
            return await resp.json()

# 💰 Купить сайт
@dp.callback_query_handler(lambda c: c.data == "buy_site")
async def buy_site(callback: types.CallbackQuery):
    invoice = await create_invoice("50")
    pay_url = invoice["result"]["pay_url"]
    invoice_id = invoice["result"]["invoice_id"]

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="💳 Оплатить", url=pay_url)
    )

    await callback.message.answer("Оплати по кнопке 👇", reply_markup=kb)
    asyncio.create_task(check_payment(callback.message.chat.id, invoice_id, "Сайт", "50$"))

# 🤖 Купить бота
@dp.callback_query_handler(lambda c: c.data == "buy_bot")
async def buy_bot(callback: types.CallbackQuery):
    invoice = await create_invoice("12.7")
    pay_url = invoice["result"]["pay_url"]
    invoice_id = invoice["result"]["invoice_id"]

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton(text="💳 Оплатить", url=pay_url)
    )

    await callback.message.answer("Оплати по кнопке 👇", reply_markup=kb)
    asyncio.create_task(check_payment(callback.message.chat.id, invoice_id, "Telegram бот", "1000 сом"))

# 🔁 Проверка оплаты
async def check_payment(chat_id, invoice_id, service_name, price):
    while True:
        await asyncio.sleep(10)
        async with aiohttp.ClientSession() as session:
            headers = {"Crypto-Pay-API-Token": CRYPTO_TOKEN}
            async with session.get(
                f"https://pay.crypt.bot/api/getInvoices?invoice_ids={invoice_id}",
                headers=headers
            ) as resp:
                result = await resp.json()
                status = result["result"]["items"][0]["status"]

        if status == "paid":
            await bot.send_message(chat_id, f"✅ Оплата получена! Услуга: {service_name}. Напишите детали заказа 👇")
            await bot.send_message(
                ADMIN_ID,
                f"💰 Новая оплата!\n\n👤 Клиент: {chat_id}\n💵 Сумма: {price}\n🛒 Услуга: {service_name}"
            )
            break

# Автоответчик
@dp.message_handler()
async def auto_reply(msg: types.Message):
    text = msg.text.lower()

    if "сайт" in text:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("💳 Оплатить сайт", callback_data="buy_site")
        )
        await msg.answer("🌐 Хотите сайт? Стоимость 50$.\nНажмите кнопку 👇", reply_markup=kb)

    elif "бот" in text:
        kb = types.InlineKeyboardMarkup().add(
            types.InlineKeyboardButton("💳 Оплатить бота", callback_data="buy_bot")
        )
        await msg.answer("🤖 Telegram бот стоит 1000 сом (~$12,7).\nНажмите кнопку 👇", reply_markup=kb)

    elif "презентация" in text:
        await msg.answer("📊 Напишите детали презентации!")

    else:
        await msg.answer("🤖 Выберите услугу ниже 👇", reply_markup=main_menu())

# Обработка текстовых отзывов
@dp.message_handler(lambda msg: msg.reply_to_message and "Пожалуйста, напишите свой отзыв" in msg.reply_to_message.text)
async def handle_review(msg: types.Message):
    review_text = msg.text.strip()
    if review_text:
        await bot.send_message(
            ADMIN_ID,
            f"📝 Новый отзыв от {msg.from_user.full_name} (@{msg.from_user.username}):\n\n{review_text}"
        )
        await msg.answer("🙏 Спасибо за отзыв!")

# ▶️ Запуск
async def main():
    await dp.start_polling()

asyncio.run(main())
