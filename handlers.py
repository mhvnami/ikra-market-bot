import os
from aiogram import Router, F
from aiogram.types import (
    Message, CallbackQuery, FSInputFile,
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "1780044773"))
SENDER_CITY_CODE = os.getenv("CDEK_SENDER_CODE", "44")  # Код города отправителя в СДЭК

router = Router()

class OrderStates(StatesGroup):
    choosing = State()  # Выбор товара
    quantity = State()  # Количество товара
    add_more = State()  # Добавление товара в корзину
    collecting_name = State()  # Сбор имени получателя
    collecting_phone = State()  # Сбор номера телефона
    collecting_address = State()  # Сбор города для доставки
    selecting_city = State()  # Выбор города
    selecting_pvz = State()  # Выбор пункта выдачи заказов (ПВЗ)
    waiting_payment = State()  # Ожидание оплаты
    confirming_order = State()  # Подтверждение заказа

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Оформить заказ")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )

# Кнопка Информация
def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 Связаться с поддержкой", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="📢 Канал с отзывами", url="https://t.me/GoldAstraShop")],
        [InlineKeyboardButton(text="📦 Оптовый заказ", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="🛒 Магазин на Авито", url="https://www.avito.ru/brands/i151719409?src=sharing")]
    ])

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в магазин «Астраханское золото»!</b>\n\n"
        "🐟 Свежая икра с доставкой по России через СДЭК.\n\n"
        "❗️Минимальный заказ — от 1 кг (можно разными товарами)\n\n"
        "Выберите действие:", reply_markup=main_menu()
    )

# Обработка команды "ℹ️ Информация"
@router.message(F.text == "ℹ️ Информация")
async def send_info(message: Message):
    await message.answer(
        "ℹ️ <b>Информация</b>\n\n"
        "Если у вас есть вопросы — <b>пишите</b>, мы отвечаем максимально быстро!\n\n"
        "👨‍💻 Техническая поддержка: <b>@oh_my_nami\n</b>"
        "📢 Новостной канал: \n"
        "<b>@GoldAstraShop</b>\n"
        "📦 Оптовые заказы (от 20 кг): <b>@oh_my_nami</b>\n\n"

        "📌 <a href='https://telegra.ph/Dobro-pozhalovat-v-magazin-Astrahanskoe-Zoloto-05-07'>Как оформить заказ?</a>\n"
        "📌 <a href='https://t.me/c/2600077572/3'>О доставке.</a>\n"
        "📌 <a href='https://t.me/c/2600077572/4'>Доедет ли икра свежей?</a>\n\n"
        "Спасибо, что выбираете <b>Астраханское Золото</b>! 🐟💛",
        reply_markup=info_menu()  # Отправляем клавиатуру с дополнительными ссылками
    )
    
# Обработка команды "🛍 Оформить заказ"
@router.message(F.text == "🛍 Оформить заказ")
async def choose_product(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await state.update_data(cart=[], total_weight=0)
    await message.answer("Выберите икру:", reply_markup=products_menu())

# Обработка выбора товара (икры)
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


# Обработка нажатия кнопки для увеличения количества
@router.callback_query(F.data.startswith("increase_"))
async def increase_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) + 1
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

# Обработка нажатия кнопки для уменьшения количества
@router.callback_query(F.data.startswith("decrease_"))
async def decrease_quantity(call: CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1]) - 1
    if qty < 1:
        qty = 1
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()

# Подтверждение выбранного количества товара
@router.callback_query(F.data == "confirm_qty")
async def confirm_quantity(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product = data["selected_product"]
    qty = data["qty"]
    product_weight = qty * 0.5  # вес одного товара (0.5 кг)
    packaging = 0.8 if data.get("cart") == [] else 0.0  # добавляем упаковку, если корзина пустая
    weight = product_weight + packaging  # общий вес товара
    new_item = {
        "name": product["name"],
        "qty": qty,
        "weight": weight,
        "sum": product["price"] * qty  # сумма за товар
    }
    cart = data.get("cart", [])
    cart.append(new_item)
    total_weight = sum(item['weight'] for item in cart)  # общий вес всех товаров
    await state.update_data(cart=cart, total_weight=total_weight)  # обновляем данные
    await call.message.answer(
        f"✅ Добавлено: {product['name']} — {qty} шт. (~{weight:.1f} кг)",
        reply_markup=next_step_menu()  # предлагаем следующие действия
    )
    await state.set_state(OrderStates.add_more)  # переходим в состояние добавления других товаров
    await call.answer()

# Добавление дополнительных товаров
@router.callback_query(F.data == "add_more")
async def add_more_items(call: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing)  # вернуться к выбору товара
    await call.message.answer("Выберите товар:", reply_markup=products_menu())  # предложим выбор товара
    await call.answer()

# Редактирование заказа (очистка корзины)
@router.callback_query(F.data == "edit_order")
async def edit_order(call: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[], total_weight=0)  # очищаем корзину
    await state.set_state(OrderStates.choosing)  # возвращаемся к выбору товара
    await call.message.answer("🧹 Заказ сброшен. Выберите товар заново:", reply_markup=products_menu())  # уведомление об очистке
    await call.answer()

# Оформление заказа (переход к сбору данных пользователя)
@router.callback_query(F.data == "proceed")
async def proceed_to_checkout(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get("total_weight", 0) < 1:  # проверка на минимальный заказ
        await call.message.answer("❗️ Минимальный заказ — от 1 кг.")
        return
    await state.set_state(OrderStates.collecting_name)  # запросим ФИО пользователя
    await call.message.answer("Введите ФИО получателя:")
    await call.answer()

# Сбор имени пользователя
@router.message(OrderStates.collecting_name)
async def collect_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())  # сохраняем ФИО
    await message.answer("Введите номер телефона:")  # запросим телефон
    await state.set_state(OrderStates.collecting_phone)

# Сбор номера телефона пользователя
@router.message(OrderStates.collecting_phone)
async def collect_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text.strip())  # сохраняем телефон
    await message.answer("Введите город доставки (для расчёта стоимости СДЭК):")  # запросим город
    await state.set_state(OrderStates.collecting_address)

# Сбор города доставки
@router.message(OrderStates.waiting_payment)
async def handle_payment(message: Message, state: FSMContext):
    if not (message.photo or message.document):
        await message.answer("❗ Пожалуйста, отправьте <b>фото</b> или <b>файл</b> с чеком.")
        return

    data = await state.get_data()
    bot = message.bot

    # Сообщение админу
    admin_chat_id = os.getenv('ADMIN_CHAT_ID')
    admin_text = (
        "📦 <b>Новый заказ!</b>\n\n"
        f"<b>Имя:</b> {data['name']}\n"
        f"<b>Телефон:</b> {data['phone']}\n"
        f"<b>Город:</b> {data['city']}\n"
        f"<b>Код ПВЗ:</b> {data.get('pvz_code', '-')}\n"
        f"<b>Общий вес:</b> {data['total_weight']} кг\n"
        f"<b>Доставка:</b> {data['delivery_price']} ₽\n"
        f"<b>Сумма к оплате:</b> {data['total_price']} ₽\n\n"
        "<b>Заказ:</b>\n"
    )
    for item in data["cart"]:
        admin_text += f"{item['name']} — {item['qty']} шт. = {item['sum']}₽\n"

    await bot.send_message(admin_chat_id, admin_text)

    if message.photo:
        await bot.send_photo(admin_chat_id, message.photo[-1].file_id, caption="🧾 Чек")
    elif message.document:
        await bot.send_document(admin_chat_id, message.document.file_id, caption="🧾 Чек")

    await message.answer("✅ Спасибо! Заказ принят, мы свяжемся с вами при отправке.")
    await state.clear()
