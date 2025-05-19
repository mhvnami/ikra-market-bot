import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from dotenv import load_dotenv

from handlers import router

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)

# Обработчик вебхука
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return web.Response(text="ok")

# Проверка работоспособности
async def health(request):
    return web.Response(text="OK")

# Настройка aiohttp
app = web.Application()
app.router.add_post('/webhook', handle_webhook)
app.router.add_get('/health', health)

# При запуске бота
async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)
    # Устанавливаем команды меню
    await bot.set_my_commands([
        BotCommand(command="start", description="🔄 Перезапуск бота"),
        BotCommand(command="info", description="ℹ️ Информация")
    ])

# При завершении
async def on_cleanup(app):
    await bot.delete_webhook()

app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

async def on_shutdown(dp):
    await cdek.close()

# Запуск
if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host='0.0.0.0', port=port)
