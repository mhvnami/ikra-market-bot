import os
from aiogram import F, Router
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand,
    BotCommandScopeDefault, MenuButtonCommands
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "1780044773"))

router = Router()

# FSM
class OrderStates(StatesGroup):
    choosing = State()
    quantity = State()
    add_more = State()
    collecting_name = State()
    collecting_phone = State()
    collecting_address = State()
    waiting_payment = State()


# Клавиатуры
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🛍 Оформить заказ")], [KeyboardButton(text="ℹ️ Информация")]],
        resize_keyboard=True
    )

def products_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Икра щуки – 2450₽ / 0.5кг", callback_data="item_1")],
        [InlineKeyboardButton(text="Икра щуки крашеная – 3000₽ / 0.5кг", callback_data="item_2")]
    ])

def quantity_buttons(qty):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{qty}"),
            InlineKeyboardButton(text=f"{qty} шт.", callback_data="none"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{qty}")
        ],
        [
            InlineKeyboardButton(text="✅ Добавить в корзину", callback_data="confirm_qty")
        ]
    ])

def next_step_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_more")],
        [InlineKeyboardButton(text="✏️ Изменить заказ", callback_data="edit_order")],
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

# Обработчики
@router.message(F.text.in_(['/start', 'start']))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в магазин «Астраханское золото»!</b>\n\n"
        "🐟 Свежая икра с доставкой по России через СДЭК.\n\n"
        "❗️Минимальный заказ — от 1 кг (можно разными товарами)\n\n"
        "Выберите действие:", reply_markup=main_menu()
    )

@router.message(F.text == "ℹ️ Информация")
async def send_info(message: Message):
    await message.answer(
        "ℹ<b>Информация</b>\n\n"
        "Если у вас есть вопросы — <b>пишите</b>, мы отвечаем максимально быстро!\n\n"
        "👨‍💻 Техническая поддержка: <b>@oh_my_nami\n</b>"
        "📢 Новостной канал: \n"
        "<b>@GoldAstraShop</b>\n"
        "📦 Оптовые заказы (от 20 кг): <b>@oh_my_nami</b>\n\n"
        "Спасибо, что выбираете <b>Астраханское Золото</b>! 🐟💛", reply_markup=info_menu()
    )

@router.message(F.text == "🛍 Оформить заказ")
async def choose_product(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await state.update_data(cart=[], total_weight=0)
    await message.answer("Выберите икру:", reply_markup=products_menu())

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
        await call.message.answer_photo(photo, caption=f"{selected_product['name']}\n{selected_product['desc']}\nЦена: {selected_product['price']}₽")
        await call.message.answer("Выберите количество банок (по 0.5 кг):", reply_markup=quantity_buttons(1))
        await state.set_state(OrderStates.quantity)
    await call.answer()

@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) + 1
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) - 1
    if qty < 1:
        qty = 1
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

@router.callback_query(F.data == "none")
async def do_nothing(call: CallbackQuery):
    await call.answer()

@router.callback_query(F.data == "confirm_qty")
async def confirm_quantity(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product = data["selected_product"]
    qty = data["qty"]
    weight = qty * 0.5
    new_item = {"name": product["name"], "qty": qty, "weight": weight, "sum": product["price"] * qty}
    cart = data.get("cart", [])
    cart.append(new_item)
    total_weight = sum(item['weight'] for item in cart)
    await state.update_data(cart=cart, total_weight=total_weight)
    await call.message.answer(f"✅ Добавлено: {product['name']} — {qty} шт. ({weight} кг)", reply_markup=next_step_menu())
    await state.set_state(OrderStates.add_more)
    await call.answer()

@router.callback_query(F.data == "add_more")
async def add_more_items(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await call.message.answer("Выберите товар:", reply_markup=products_menu())
    await call.answer()

@router.callback_query(F.data == "edit_order")
async def edit_order(call: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[], total_weight=0)
    await state.set_state(OrderStates.choosing)
    await call.message.answer("🧹 Заказ сброшен. Выберите товар заново:", reply_markup=products_menu())
    await call.answer()

@router.callback_query(F.data == "proceed")
async def proceed_to_checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("total_weight", 0) < 1:
        await call.message.answer("❗️ Минимальный заказ — от 1 кг.")
        return
    await state.set_state(OrderStates.collecting_name)
    await call.message.answer("Введите ФИО получателя:")
    await call.answer()

@router.message(OrderStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Введите номер телефона:")
    await state.set_state(OrderStates.collecting_phone)

@router.message(OrderStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())
    await message.answer("Введите адрес доставки (СДЭК):")
    await state.set_state(OrderStates.collecting_address)

@router.message(OrderStates.collecting_address)
async def collect_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text.strip())
    data = await state.get_data()
    text = "🧾 <b>Ваш заказ:</b>\n"
    total = 0
    for item in data['cart']:
        text += f"{item['name']} — {item['qty']} шт. ({item['weight']} кг) = {item['sum']}₽\n"
        total += item['sum']
    text += f"\n<b>Общий вес:</b> {data['total_weight']} кг\n<b>Сумма:</b> {total} ₽"
    await message.answer(text)
    await message.answer("Выберите способ оплаты:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить по реквизитам", callback_data="pay_manual")]
    ]))
    await state.set_state(OrderStates.waiting_payment)

@router.callback_query(F.data == "pay_manual")
async def pay_manual(call: CallbackQuery):
    await call.message.answer("💳 Оплата по реквизитам:\n<b>Карта:</b> 2200700974216722\n<b>Имя:</b> Анатолий Владимирович\n\nПосле оплаты отправьте чек.")
    await call.answer()

@router.message(OrderStates.waiting_payment)
async def receive_payment(message: Message, state: FSMContext):
    data = await state.get_data()
    bot = message.bot
    if message.photo or message.document:
        await message.answer("✅ Чек получен.")
        admin_text = "📦 <b>Новый заказ!</b>\n"
        for item in data['cart']:
            admin_text += f"{item['name']} — {item['qty']} шт. = {item['sum']}₽\n"
        admin_text += f"\n<b>Имя:</b> {data['name']}\n<b>Телефон:</b> {data['phone']}\n<b>Адрес:</b> {data['address']}"
        await bot.send_message(ADMIN_ID, admin_text)
        if message.photo:
            await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption="Чек")
        elif message.document:
            await bot.send_document(ADMIN_ID, message.document.file_id, caption="Чек")
        await state.clear()
    else:
        await message.answer("❗ Пожалуйста, отправьте фото или файл чека.")


