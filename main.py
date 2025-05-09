import os
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

from handlers import router  # Импортируем router, не dp

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO)

# Создание бота и диспетчера
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
storage = MemoryStorage()
dp = Dispatcher(storage=storage)
dp.include_router(router)  # Подключаем маршрутизатор

# Обработчик вебхука
async def handle_webhook(request):
    update = await request.json()
    await dp.feed_raw_update(bot, update)
    return web.Response(text="ok")

# Настройка aiohttp
app = web.Application()
app.router.add_post('/webhook', handle_webhook)

async def on_startup(app):
    await bot.set_webhook(WEBHOOK_URL)

async def on_cleanup(app):
    await bot.delete_webhook()

app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    web.run_app(app, host='0.0.0.0', port=port)
