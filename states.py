from aiogram.fsm.state import State, StatesGroup

class DeliveryStates(StatesGroup):
    waiting_for_city = State()
    waiting_for_pickup_point = State()
    confirm_delivery = State()
