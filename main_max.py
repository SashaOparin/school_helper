import asyncio
import logging
import os

from dotenv import load_dotenv

from maxapi import Bot, Dispatcher, F
from maxapi.types import Command

from db.database import create_tables
from max_handlers.gpt_handlers import ask_gpt, start_gpt
from max_handlers.main_menu_handlers import back, change_class, get_users_class, settings
from max_handlers.max_states import MaxStates
from max_handlers.start_handler import start
from max_handlers.trening_handlers import hp_kontrol, show_kontrol_answers, start_kontrol
from max_handlers.victorina_handlers import get_answer, set_bot, victor_answer, victor_topic

load_dotenv()
logging.basicConfig(level=logging.INFO)

bot = Bot(token=os.getenv("MAX_TOKEN"))
dp = Dispatcher()
set_bot(bot)


# Создаем таблицы при старте MAX-бота
@dp.on_started()
async def on_started():
    await create_tables(None)


# Регистрируем обработчики, как в Telegram-версии
dp.message_created.register(start, Command("start"))

dp.message_created.register(get_users_class, F.message.body.text, MaxStates.get_class)
dp.message_callback.register(settings, F.callback.payload == "settings", MaxStates.main_menu)
dp.message_callback.register(change_class, F.callback.payload == "change_class", MaxStates.settings)

dp.message_callback.register(start_gpt, F.callback.payload == "gpt_ask", MaxStates.main_menu)
dp.message_created.register(ask_gpt, F.message.body.text, MaxStates.gpt)

dp.message_callback.register(victor_topic, F.callback.payload == "victor", MaxStates.main_menu)
dp.message_created.register(victor_answer, F.message.body.text, MaxStates.get_victor_topic)
dp.message_callback.register(
    get_answer,
    F.callback.payload.startswith("victor_answer:"),
    MaxStates.get_victor_answer,
)

dp.message_callback.register(start_kontrol, F.callback.payload == "kontrol", MaxStates.main_menu)
dp.message_created.register(hp_kontrol, F.message.body.text, MaxStates.kontrol)
dp.message_callback.register(
    show_kontrol_answers,
    F.callback.payload == "show_kontrol_answers",
    MaxStates.get_kontrol_answer,
)

dp.message_callback.register(back, F.callback.payload == "back")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
