import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, BotCommand, BotCommandScopeDefault, MenuButtonCommands 
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "1780044773"))

bot = Bot(
    token=BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

# ---- FSM состояния ----
class OrderStates(StatesGroup):
    choosing = State()  # Выбор товара
    quantity = State()  # Ввод количества
    add_more = State()  # Добавить еще товар
    collecting_name = State()  # Ввод ФИО
    collecting_phone = State()  # Ввод телефона
    collecting_address = State()  # Ввод адреса
    waiting_payment = State()  # Ожидание оплаты

# ---- Кнопки ----
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Оформить заказ")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )

def products_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Икра щуки – 2450₽ / 0.5кг", callback_data="item_1")],
        [InlineKeyboardButton(text="Икра щуки крашеная – 3000₽ / 0.5кг", callback_data="item_2")]
    ])

def next_step_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_more")],
        [InlineKeyboardButton(text="✅ Оформить заказ", callback_data="proceed")]
    ])

def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Инструкция по заказу", url="https://telegra.ph/Dobro-pozhalovat-v-magazin-Astrahanskoe-Zoloto-05-07")],
        [InlineKeyboardButton(text="👨‍💼 Связаться с поддержкой", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="📢 Канал с отзывами", url="https://t.me/GoldAstraShop")],
        [InlineKeyboardButton(text="📦 Оптовый заказ", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="🛒 Магазин на Авито", url="https://www.avito.ru/brands/i151719409?src=sharing")]
    ])

# ---- Обработчики ----

@dp.message(F.text.in_(['/start', 'start']))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в магазин «Астраханское золото»!</b>\n\n"
        "🐟 Свежая икра с доставкой по России через СДЭК.\n\n"
        "❗️Минимальный заказ — от 1 кг (можно разными товарами)\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

@dp.message(F.text == "ℹ️ Информация")
async def send_info(message: Message):
    await message.answer(
        "ℹ️ <b>Информация</b>\n\n"
        "Если у вас есть вопросы — <b>пишите</b>, мы отвечаем максимально быстро!\n\n"
        "👨‍💻 Техническая поддержка: <b>@oh_my_nami\n</b>"
        "📢 Новостной канал: \n"
        "<b>@GoldAstraShop</b>\n"
        "📦 Оптовые заказы (от 20 кг): <b>@oh_my_nami</b>\n\n"
        "Спасибо, что выбираете <b>Астраханское Золото</b>! 🐟💛",
        reply_markup=info_menu()  # Привязываем клавиатуру с кнопками
    )

@dp.message(F.text == "🛍 Оформить заказ")
async def choose_product(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await state.update_data(cart=[], total_weight=0)
    await message.answer("Выберите икру:", reply_markup=products_menu())

@dp.callback_query(F.data.startswith("item_"))
async def handle_item(call: CallbackQuery, state: FSMContext):
    item = call.data.split("_")[1]
    product_info = {
        "1": {
            "name": "🐟 <b>Икра щуки</b>",
            "price": 2450,
            "photo": "images/pike.jpg",
            "desc": (
                "✨ <b>Охлаждённая, слабосоленая</b>\n"
                "Состав: <b>икра щуки, соль</b>.\n"
                "Вес: <b>0.5 кг</b>\n\n"
                "🔋 <b>КБЖУ (на 100 г):</b>\n"
                "• Белки: <b>26 г</b>\n"
                "• Жиры: <b>3 г</b>\n"
                "• Энергетическая ценность: <b>131 ккал</b> / 548 кДж\n\n"
                "👌 <b>Особенности:</b>\n"
                "Икра щуки — это деликатес, известный своим насыщенным вкусом и богатым составом. "
                "Она станет отличным дополнением к любому столу и подарит вам незабываемые вкусовые ощущения."
            )
        },
        "2": {
            "name": "🎨 <b>Икра щуки крашеная</b>",
            "price": 3000,
            "photo": "images/pike_colored.jpg",
            "desc": (
                "✨ <b>Состав:</b> икра щуки, соль, краситель ВАРЭЛЬ.\n"
                "Вес: <b>0.5 кг</b>\n\n"
                "🔋 <b>КБЖУ (на 100 г):</b>\n"
                "• Белки: <b>26 г</b>\n"
                "• Жиры: <b>3 г</b>\n"
                "• Энергетическая ценность: <b>131 ккал</b> / 548 кДж\n\n"
                "👌 <b>Особенности:</b>\n"
                "Насыщенная и яркая икра щуки крашеная привнесет в вашу трапезу яркие краски и вкус! "
                "Идеальный вариант для тех, кто хочет порадовать себя или близких необычным и полезным деликатесом."
            )
        }
    }

    if item in product_info:
        selected_product = product_info[item]
        await state.update_data(selected_product=selected_product)

        photo = FSInputFile(selected_product["photo"])
        await call.message.answer_photo(
            photo=photo,
            caption=f"<b>{selected_product['name']}</b>\n{selected_product['desc']}\nЦена: {selected_product['price']}₽ / 0.5кг"
        )
        await call.message.answer("Введите количество банок (по 0.5 кг):")
        await state.set_state(OrderStates.quantity)
        await call.answer()

    else:
        await call.message.answer("❗️Товар не найден.")

@dp.message(OrderStates.quantity)
async def process_quantity(message: Message, state: FSMContext):
    try:
        qty = int(message.text.strip())
        data = await state.get_data()
        product = data["selected_product"]
        weight = qty * 0.5
        new_item = {
            "name": product["name"],
            "qty": qty,
            "weight": weight,
            "sum": product["price"] * qty
        }

        cart = data.get("cart", [])
        cart.append(new_item)
        total_weight = sum(item['weight'] for item in cart)

        await state.update_data(cart=cart, total_weight=total_weight)
        await message.answer(
            f"✅ Добавлено: {product['name']} — {qty} шт. ({weight} кг)\n\n"
            f"Текущий вес: {total_weight} кг",
            reply_markup=next_step_menu()
        )
        await state.set_state(OrderStates.add_more)
    except ValueError:
        await message.answer("Введите число — количество банок.")

@dp.callback_query(F.data == "add_more")
async def add_more_items(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await call.message.answer("Выберите товар:", reply_markup=products_menu())
    await call.answer()

@dp.callback_query(F.data == "proceed")
async def proceed_to_checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("total_weight", 0) < 1:
        await call.message.answer("❗️Минимальный заказ — от 1 кг. Добавьте ещё товар.")
        return
    await state.set_state(OrderStates.collecting_name)
    await call.message.answer("Введите ФИО получателя:")
    await call.answer()

@dp.message(OrderStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите номер телефона:")
    await state.set_state(OrderStates.collecting_phone)

@dp.message(OrderStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("Введите адрес доставки (СДЭК):")
    await state.set_state(OrderStates.collecting_address)

@dp.message(OrderStates.collecting_address)
async def collect_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    data = await state.get_data()

    text = "🧾 <b>Ваш заказ:</b>\n"
    total = 0
    for item in data['cart']:
        text += f"{item['name']} — {item['qty']} шт. ({item['weight']} кг) = {item['sum']}₽\n"
        total += item['sum']

    text += f"\n<b>Общий вес:</b> {data['total_weight']} кг"
    text += f"\n<b>Сумма к оплате:</b> {total} ₽"

    await message.answer(text)
    await message.answer(
        "Выберите способ оплаты:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить по реквизитам", callback_data="pay_manual")]
        ])
    )
    await state.set_state(OrderStates.waiting_payment)

@dp.callback_query(F.data == "pay_manual")
async def pay_manual(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "💳 Оплата по реквизитам:\n\n"
        "<b>Карта Тинькофф:</b> 2200700974216722\n"
        "<b>Получатель:</b>Анатолий Владимирович\n\n"
        "<b>После оплаты пришлите чек сюда. Мы проверим и примем заказ в работу</b>."
    )
    await call.answer()

@dp.message(OrderStates.waiting_payment)
async def receive_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.photo or message.document:
        await state.update_data(user_id=message.from_user.id)
        await message.answer("✅ Чек получен. Ожидайте подтверждения.")
        admin_text = f"📦 <b>Новый заказ!</b>\n\n"
        for item in data['cart']:
            admin_text += f"{item['name']} — {item['qty']} шт. = {item['sum']}₽\n"
        admin_text += (
            f"\n<b>Вес:</b> {data['total_weight']} кг"
            f"\n<b>Сумма:</b> {sum(i['sum'] for i in data['cart'])} ₽"
            f"\n\n<b>Имя:</b> {data['name']}"
            f"\n<b>Телефон:</b> {data['phone']}"
            f"\n<b>Адрес (СДЭК):</b> {data['address']}"
        )

        await bot.send_message(chat_id=ADMIN_ID, text=admin_text)

        if message.photo:
            photo_file_id = message.photo[-1].file_id
            await bot.send_photo(chat_id=ADMIN_ID, photo=photo_file_id, caption="Чек")
        elif message.document:
            await bot.send_document(chat_id=ADMIN_ID, document=message.document.file_id, caption="Чек")

        await state.clear()
    else:
        await message.answer("❗ Пожалуйста, отправьте фото или файл чека.")

@dp.startup()
async def on_startup(dispatcher):
    # Установка меню команд
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="🔄 Перезапуск бота"),
            BotCommand(command="info", description="ℹ️ Информация")
        ],
        scope=BotCommandScopeDefault()
    )

    # Включение постоянной кнопки меню
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
@dp.message(F.text.startswith("/трек"))
async def send_tracking_code(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("⛔️ Команда доступна только администратору.")
        return

    parts = message.text.strip().split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("❗ Формат: /трек <user_id> <трек-номер>")
        return

    try:
        user_id = int(parts[1])
        tracking_number = parts[2]

        await bot.send_message(
            chat_id=user_id,
            text=(
                "✅ <b>Ваш заказ передан в доставку!</b>\n\n"
                f"📦 Трек-номер для отслеживания:\n<code>{tracking_number}</code>\n\n"
                "Вы можете отслеживать заказ через сайт СДЭК."
            )
        )
        await message.answer("✅ Трек-номер отправлен пользователю.")

    except Exception as e:
        await message.answer(f"❗ Ошибка при отправке: {e}")
        

# --- Запуск бота ---

async def on_startup():
    # Установка меню команд
    await bot.set_my_commands(
        commands=[
            BotCommand(command="start", description="🔄 Перезапуск бота"),
            BotCommand(command="info", description="ℹ️ Информация")
        ],
        scope=BotCommandScopeDefault()
    )
    # Включение постоянной кнопки меню
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

async def main():
    await on_startup()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL") + WEBHOOK_PATH

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="🔄 Перезапуск бота"),
            BotCommand(command="info", description="ℹ️ Информация")
        ],
        scope=BotCommandScopeDefault()
    )
    await bot.set_chat_menu_button(menu_button=MenuButtonCommands())

async def on_shutdown(app):
    await bot.delete_webhook()

async def main():
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)

    return app

import asyncio

if __name__ == "__main__":
    import asyncio

    app = asyncio.run(main())  # создаём приложение
    web.run_app(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))  # запускаем сервер






