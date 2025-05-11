import os
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "1780044773"))
SENDER_CITY_CODE = os.getenv("CDEK_SENDER_CODE", "44")  # Код города отправителя в СДЭК

router = Router()

# Состояния
class OrderStates(StatesGroup):
    choosing = State()
    quantity = State()
    add_more = State()
    collecting_name = State()
    collecting_phone = State()
    collecting_address = State()
    selecting_city = State()
    selecting_pvz = State()
    waiting_payment = State()
    confirming_order = State()

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Оформить заказ")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )

# Меню Информация
def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 Связаться с поддержкой", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="📢 Канал с отзывами", url="https://t.me/GoldAstraShop")],
        [InlineKeyboardButton(text="📦 Оптовый заказ", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="🛒 Магазин на Авито", url="https://www.avito.ru/brands/i151719409?src=sharing")]
    ])

# Меню выбора продуктов
def products_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Икра щуки", callback_data="item_1")],
        [InlineKeyboardButton(text="🎨 Икра щуки крашеная", callback_data="item_2")]
    ])

# Кнопки выбора количества
def quantity_buttons(qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{qty}"),
            InlineKeyboardButton(text=f"{qty}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{qty}")
        ],
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_qty")]
    ])

# Кнопки после добавления товара
def next_step_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_more")],
        [InlineKeyboardButton(text="✏️ Изменить заказ", callback_data="edit_order")],
        [InlineKeyboardButton(text="✅ Перейти к оформлению", callback_data="proceed")]
    ])

# Команда /start
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в магазин «Астраханское золото»!</b>\n\n"
        "🐟 Свежая икра с доставкой по России через СДЭК.\n\n"
        "❗️Минимальный заказ — от 1 кг (можно разными товарами)\n\n"
        "Выберите действие:", reply_markup=main_menu()
    )

# Информация
@router.message(F.text == "ℹ️ Информация")
async def send_info(message: Message):
    await message.answer(
        "ℹ️ <b>Информация</b>\n\n"
        "Если у вас есть вопросы — <b>пишите</b>, мы отвечаем максимально быстро!\n\n"
        "👨‍💻 Техническая поддержка: <b>@oh_my_nami</b>\n"
        "📢 Новостной канал: <b>@GoldAstraShop</b>\n"
        "📦 Оптовые заказы (от 20 кг): <b>@oh_my_nami</b>\n\n"
        
        "📌 <a href='https://telegra.ph/Dobro-pozhalovat-v-magazin-Astrahanskoe-Zoloto-05-07'>Как оформить заказ?</a>\n"
        "📌 <a href='https://t.me/c/2600077572/3'>О доставке.</a>\n"
        "📌 <a href='https://t.me/c/2600077572/4'>Доедет ли икра свежей?</a>\n\n"
        "Спасибо, что выбираете <b>Астраханское Золото</b>! 🐟💛",
        reply_markup=info_menu()
    )

# Оформить заказ
@router.message(F.text == "🛍 Оформить заказ")
async def choose_product(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await state.update_data(cart=[], total_weight=0)
    await message.answer("Выберите икру:", reply_markup=products_menu())

# Выбор товара
@router.callback_query(F.data.startswith("item_"))
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

    selected_product = product_info.get(item)
    if selected_product:
        await state.update_data(selected_product=selected_product, qty=1)
        photo = FSInputFile(selected_product["photo"])
        await call.message.answer_photo(
            photo,
            caption=f"{selected_product['name']}\n<b>Цена:</b> {selected_product['price']}₽ за 0.5 кг"
        )
        await call.message.answer("Выберите количество банок (по 0.5 кг):", reply_markup=quantity_buttons(1))
        await state.set_state(OrderStates.quantity)
    await call.answer()

# Изменение количества
@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) + 1
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) - 1
    qty = max(qty, 1)
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

# Подтверждение количества
@router.callback_query(F.data == "confirm_qty")
async def confirm_quantity(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product = data["selected_product"]
    qty = data["qty"]
    product_weight = qty * 0.5
    packaging = 0.8 if not data.get("cart") else 0.0
    weight = product_weight + packaging
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
    await call.message.answer(
        f"✅ Добавлено: {product['name']} — {qty} шт. (~{weight:.1f} кг)",
        reply_markup=next_step_menu()
    )
    await state.set_state(OrderStates.add_more)
    await call.answer()

# Повторный выбор товара
@router.callback_query(F.data == "add_more")
async def add_more_items(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await call.message.answer("Выберите товар:", reply_markup=products_menu())
    await call.answer()

# Очистка заказа
@router.callback_query(F.data == "edit_order")
async def edit_order(call: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[], total_weight=0)
    await state.set_state(OrderStates.choosing)
    await call.message.answer("🧹 Заказ сброшен. Выберите товар заново:", reply_markup=products_menu())
    await call.answer()

# Перейти к оформлению
@router.callback_query(F.data == "proceed")
async def proceed_to_checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("total_weight", 0) < 1:
        await call.message.answer("❗️ Минимальный заказ — от 1 кг.")
        return
    await state.set_state(OrderStates.collecting_name)
    await call.message.answer("Введите ФИО получателя:")
    await call.answer()

# Сбор данных пользователя
@router.message(OrderStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите номер телефона:")
    await state.set_state(OrderStates.collecting_phone)

@router.message(OrderStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("Введите город доставки (для расчёта стоимости СДЭК):")
    await state.set_state(OrderStates.collecting_address)

# Принятие чека
@router.message(OrderStates.waiting_payment)
async def handle_payment(message: Message, state: FSMContext):
    if not (message.photo or message.document):
        await message.answer("❗ Пожалуйста, отправьте <b>фото</b> или <b>файл</b> с чеком.")
        return

    data = await state.get_data()
    bot = message.bot

    admin_chat_id = os.getenv('ADMIN_CHAT_ID', ADMIN_ID)
    admin_text = (
        "📦 <b>Новый заказ!</b>\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Город:</b> {data.get('city', '-')}\n"
        f"<b>Код ПВЗ:</b> {data.get('pvz_code', '-')}\n"
        f"<b>Общий вес:</b> {data['total_weight']} кг\n"
        f"<b>Доставка:</b> {data.get('delivery_price', '—')} ₽\n"
        f"<b>Сумма к оплате:</b> {data.get('total_price', '—')} ₽\n\n"
        "<b>Заказ:</b>\n"
    )
    for item in data.get("cart", []):
        admin_text += f"{item['name']} — {item['qty']} шт. = {item['sum']}₽\n"

    await bot.send_message(admin_chat_id, admin_text)

    if message.photo:
        await bot.send_photo(admin_chat_id, message.photo[-1].file_id, caption="🧾 Чек")
    elif message.document:
        await bot.send_document(admin_chat_id, message.document.file_id, caption="🧾 Чек")

    await message.answer("✅ Спасибо! Заказ принят, мы свяжемся с вами при отправке.")
    await state.clear()
