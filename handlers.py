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
from utils.cdek import CDEKClient

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CDEK_CLIENT_ID = os.getenv("CDEK_CLIENT_ID")
CDEK_CLIENT_SECRET = os.getenv("CDEK_CLIENT_SECRET")
SENDER_CITY_CODE = os.getenv("SENDER_CITY_CODE")
router = Router()

# Состояния заказа
class OrderStates(StatesGroup):
    choosing = State()
    quantity = State()
    add_more = State()
    collecting_name = State()
    collecting_phone = State()
    collecting_city = State()  # Ввод города для поиска ПВЗ
    choosing_pvz = State()     # Выбор ПВЗ
    waiting_payment = State()
    awaiting_order_confirmation = State()
    waiting_payment_confirmation = State()
    entering_track_number = State() 

# Главное меню
def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛍 Оформить заказ")],
            [KeyboardButton(text="ℹ️ Информация")]
        ],
        resize_keyboard=True
    )

# Информационное меню
def info_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👨‍💼 Поддержка", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="📢 Отзывы", url="https://t.me/GoldAstraShop")],
        [InlineKeyboardButton(text="📦 Опт (от 20 кг)", url="https://t.me/oh_my_nami")],
        [InlineKeyboardButton(text="🛒 Магазин на Авито", url="https://www.avito.ru/brands/i151719409?src=sharing")],
        [InlineKeyboardButton(text="❓ Как заказать?", url="https://telegra.ph/Dobro-pozhalovat-v-magazin-Astrahanskoe-Zoloto-05-07")]
    ])

# Команда /start
@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 <b>Добро пожаловать в магазин «Астраханское золото»!</b>\n\n"
        "🐟 Свежая икра с доставкой по России через СДЭК.\n"
        "❗️ Минимальный заказ — от 1 кг (можно разными товарами)\n\n"
        "Выберите действие:",
        reply_markup=main_menu()
    )

# Инфо
@router.message(F.text == "ℹ️ Информация")
async def send_info(message: Message):
    await message.answer(
        "ℹ️ <b>Информация</b>\n\n"
        "Если у вас есть вопросы — <b>пишите</b>, мы отвечаем максимально быстро!\n\n"
        "👨‍💻 Техническая поддержка: <b>@oh_my_nami\n</b>"
        "📢 Новостной канал: \n"
        "<b>@GoldAstraShop</b>\n"
        "📦 Оптовые заказы (от 20 кг): <b>@oh_my_nami</b>\n\n"
        
        "<a href='https://t.me/c/2600077572/3'>📦 О доставке</a>\n"
        "<a href='https://t.me/c/2600077572/4'>❄️ Доедет ли икра свежей?</a>",
        "Спасибо, что выбираете <b>Астраханское Золото</b>! 🐟💛",
        reply_markup=info_menu()
    )
# Меню выбора продуктов
def products_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🐟 Икра щуки – 2450₽ / 0.5кг", callback_data="item_1")],
        [InlineKeyboardButton(text="🎨 Икра щуки крашеная – 3000₽ / 0.5кг", callback_data="item_2")]
    ])

# Кнопки количества
def quantity_buttons(qty: int):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➖", callback_data=f"decrease_{qty}"),
            InlineKeyboardButton(text=f"{qty}", callback_data="noop"),
            InlineKeyboardButton(text="➕", callback_data=f"increase_{qty}")
        ],
        [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_qty")]
    ])

# Кнопки после добавления
def next_step_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ещё", callback_data="add_more")],
        [InlineKeyboardButton(text="✏️ Изменить заказ", callback_data="edit_order")],
        [InlineKeyboardButton(text="✅ Перейти к оформлению", callback_data="proceed")]
    ])
product_info = {
    "1": {
        "name": "🐟 <b>Икра щуки</b>",
        "price":2450,
        "photo": "images/pike.jpg",
        "desc": (
            "✨ <b>Охлаждённая, слабосоленая</b>\n"
            "Состав: <b>икра щуки, соль</b>.\n"
            "Вес: <b>0.5 кг</b>\n\n"
            "🔋 <b>КБЖУ (на 100 г):</b>\n"
            "• Белки: <b>26 г</b>\n"
            "• Жиры: <b>3 г</b>\n"
            "• Калорийность: <b>131 ккал</b>\n\n"
            "👌 <b>Описание:</b>\n"
            "Натуральная икра щуки — деликатес с насыщенным вкусом и нежной текстурой. "
            "Подходит к любому блюду и украшает любой стол."
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
            "• Калорийность: <b>131 ккал</b>\n\n"
            "👌 <b>Описание:</b>\n"
            "Классическая икра щуки с добавлением красителя для более насыщенного вида. "
            "Яркий вкус и выгодный вариант для сервировки праздничного стола."
        )
    }
}

@router.message(F.text == "🛍 Оформить заказ")
async def choose_product(message: Message, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await state.update_data(cart=[], total_weight=0)
    await message.answer("Выберите товар:", reply_markup=products_menu())


@router.callback_query(F.data.startswith("item_"))
async def handle_item(call: CallbackQuery, state: FSMContext):
    item_id = call.data.split("_")[1]
    selected = product_info.get(item_id)
    if not selected:
        await call.answer("Товар не найден.")
        return

    await state.update_data(selected_product=selected, qty=1)

    photo = FSInputFile(selected["photo"])
    await call.message.answer_photo(
        photo,
        caption=f"{selected['name']}\n<b>Цена:</b> {selected['price']}₽ / 0.5 кг\n\n{selected['desc']}"
    )
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
    qty = max(1, int(call.data.split("_")[1]) - 1)
    await state.update_data(qty=qty)
    await call.message.edit_reply_markup(reply_markup=quantity_buttons(qty))
    await call.answer()


@router.callback_query(F.data == "confirm_qty")
async def confirm_quantity(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    product = data["selected_product"]
    qty = data["qty"]
    weight = qty * 0.5
    # Упаковка учитывается скрытно
    packaging_weight = 0.8 if not data.get("cart") else 0
    full_weight = weight + packaging_weight

    new_item = {
        "name": product["name"],
        "qty": qty,
        "weight": full_weight,
        "sum": product["price"] * qty
    }

    cart = data.get("cart", [])
    cart.append(new_item)

    total_weight = sum(i["weight"] for i in cart)
    await state.update_data(cart=cart, total_weight=total_weight)

    await call.message.answer(
        f"✅ Добавлено в заказ: {product['name']} — {qty} шт.",
        reply_markup=next_step_menu()
    )
    await state.set_state(OrderStates.add_more)
    await call.answer()
import requests

# ——— Добавить ещё товар ———
@router.callback_query(F.data == "add_more")
async def add_more_items(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.choosing)
    await callback.message.answer("Выберите товар:", reply_markup=products_menu())
    await callback.answer()

# ——— Изменить заказ ——— (удалим всё и начнём сначала)
@router.callback_query(F.data == "edit_order")
async def edit_order(callback: CallbackQuery, state: FSMContext):
    await state.update_data(cart=[], total_weight=0)
    await callback.message.answer("Корзина очищена. Выберите товар заново:", reply_markup=products_menu())
    await state.set_state(OrderStates.choosing)
    await callback.answer()

# ——— Переход к оформлению ———
@router.callback_query(F.data == "proceed")
async def proceed_to_checkout(callback: CallbackQuery, state: FSMContext):
    await state.set_state(OrderStates.collecting_name)
    await callback.message.answer("Введите ваше <b>ФИО</b>:")
    await callback.answer()

@router.message(OrderStates.collecting_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.collecting_phone)
    await message.answer(
        "Введите ваш <b>номер телефона</b>: (например, +79001234567)"
    )

# ——— Телефон ———
@router.message(OrderStates.collecting_phone)
async def get_phone(message: Message, state: FSMContext):
    phone = re.sub(r"[^\d+]", "", message.text.strip())  # удалим пробелы и лишние символы
    if not re.fullmatch(r"\+7\d{10}", phone):
        await message.answer("Введите номер в формате +7XXXXXXXXXX")
        return

    await state.update_data(phone=phone)
    await state.set_state(OrderStates.collecting_city)
    await message.answer("Введите <b>название города</b>, чтобы найти ПВЗ СДЭК:")

 # ——— Ввод города и показ ПВЗ ———
@router.message(OrderStates.collecting_city)
async def get_city(message: Message, state: FSMContext):
    city = message.text.strip()
    pvz_list = get_delivery_points(city)

    if not pvz_list:
        await message.answer("Не удалось найти ПВЗ в этом городе. Попробуйте снова:")
        return

    await state.update_data(city=city, pvz_list=pvz_list[:10])  # покажем первые 10
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{p['address']}",
                callback_data=f"pvz_{p['code']}"
            )] for p in pvz_list[:10]
        ]
    )
    await message.answer("Выберите ближайший пункт СДЭК:", reply_markup=keyboard)
    await state.set_state(OrderStates.choosing_pvz)

# ——— Подтверждение ПВЗ ———
@router.callback_query(F.data.startswith("pvz_"))
async def select_pvz(callback: CallbackQuery, state: FSMContext):
    code = callback.data.split("_")[1]
    data = await state.get_data()
    chosen = next((p for p in data["pvz_list"] if p["code"] == code), None)

    if not chosen:
        await callback.message.answer("Ошибка выбора ПВЗ. Попробуйте снова.")
        return

    await state.update_data(pvz_code=code, pvz_address=chosen["address"])
    await callback.message.answer(
        f"✅ Выбран ПВЗ: {chosen['address']}\n\nПодтвердите заказ?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order")],
            [InlineKeyboardButton(text="🔙 Отмена", callback_data="cancel_order")]
        ])
    )
    await state.set_state(OrderStates.confirming)
    await callback.answer()
   
from aiogram.types import InputMediaPhoto

@router.callback_query(F.data == "confirm_order")
async def confirm_order(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    name = data.get("name")
    phone = data.get("phone")
    city = data.get("city")
    pvz_address = data.get("pvz_address")
    cart = data.get("cart", [])
    total_weight = 0
    total_price = 0

    product_lines = []
    for item in cart:
        name_ = item["name"]
        qty = item["qty"]
        price = item["sum"] // item["qty"]
        weight = item["weight"]
        total_item_price = price * qty
        total_item_weight = weight * qty
        total_price += item["sum"]
        total_weight += item["weight"]
        product_lines.append(f"{name_} — {qty} шт.")

    cart_summary = "\n".join(product_lines)
    user_text = (
        f"<b>Ваш заказ:</b>\n"
        f"{cart_summary}\n\n"
        f"📦 Город: {city}\n"
        f"🏪 ПВЗ: {pvz_address}\n"
        f"👤 Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Сумма: {total_price} ₽\n"
    )
    await state.update_data(address=pvz_address)
    await state.set_state(OrderStates.awaiting_order_confirmation)

    keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Подтвердить заказ", callback_data="submit_order"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Отменить", callback_data="cancel_order"
            )
        ]
    ]
)

    await callback.message.answer(
        "💳 <b>Оплата</b>\n\n"
        "🧊 В каждую упаковку добавлен хладоэлемент, икра доезжает в идеальном состоянии.\n"
        "📅 Срок доставки зависит от города (3–5 дней в среднем).\n"
        "<b>Переведите сумму на карту:</b>\n"
        "🔹 <b>2200 7009 7421 6722</b>\n"
        "🔹 <b>Анатолий Владимирович</b>\n\n"
        "После оплаты отправьте <b>чек (фото или файл)</b> в этот чат."
    )
    await state.set_state(OrderStates.waiting_payment_confirmation)
    await callback.answer()

@router.message(OrderStates.waiting_payment_confirmation)
async def handle_payment(message: Message, state: FSMContext):
    if not (message.photo or message.document):
        await message.answer(
            "❗ Пожалуйста, отправьте <b>фото</b> или <b>файл</b> с чеком."
        )
        return
    
    await message.answer("✅ Спасибо за заказ. Ожидайте подтверждение от администратора.")

    # Сохраняем user_id
    await state.update_data(user_id=message.from_user.id)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"admin_confirm:{message.from_user.id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"admin_reject:{message.from_user.id}")
        ]
    ])

    caption = f"📩 Новый заказ от @{message.from_user.username or 'без ника'} (ID: {message.from_user.id})\n" \
              f"💳 Чек получен."

    if message.photo:
        await message.bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, reply_markup=kb)
    elif message.document:
        await message.bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, reply_markup=kb)

    await state.set_state(OrderStates.waiting_admin_response)

# Админ нажимает Подтвердить → переходит к вводу трека
@router.callback_query(F.data.startswith("admin_confirm:"))
async def admin_start_track_input(callback: CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[1])
    await state.update_data(confirming_user=user_id)
    await callback.message.edit_text("✏️ Введите трек-номер для отправки покупателю:")
    await state.set_state(OrderStates.entering_track_number)
    await callback.answer()

# Админ вводит трек-номер
@router.message(OrderStates.entering_track_number)
async def handle_track_number_input(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("confirming_user")
    track_number = message.text.strip()

    # Создаем клиента СДЭК
    cdek_client = CDEKClient()

    # Получаем данные или ставим заглушки
    sender_city_code = data.get("sender_city_code", 44)  # подставь реальные данные
    receiver_city_code = data.get("receiver_city_code", 44)
    receiver_address = data.get("receiver_address", "Адрес получателя")
    receiver_name = data.get("receiver_name", "Имя Получателя")
    receiver_phone = data.get("receiver_phone", "+79001234567")

    # Создаем отправление
    shipment_response = await cdek_client.create_shipment(
        sender_city_code=sender_city_code,
        receiver_city_code=receiver_city_code,
        receiver_address=receiver_address,
        receiver_name=receiver_name,
        receiver_phone=receiver_phone,
        order_number=f"ORDER-{user_id}-{track_number}",
        package_weight=500
    )

    await cdek_client.close()

    # Проверяем ответ и уведомляем пользователя
    if shipment_response.get("uuid"):
        await message.bot.send_message(
            user_id,
            f"✅ Ваш заказ подтверждён!\n"
            f"📦 Трек-номер: <b>{track_number}</b>\n"
            f"🚚 Отправление создано в СДЭК."
        )
        await message.answer("📨 Трек-номер отправлен покупателю, отправление создано.")
    else:
        await message.bot.send_message(
            user_id,
            "⚠️ Заказ подтверждён, но не удалось создать отправление. Администратор свяжется с вами."
        )
        await message.answer("⚠️ Ошибка при создании отправления.")

    # Очистка состояния
    await state.clear()
