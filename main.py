import logging
import os
from random import choice
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    PicklePersistence,
)
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

GET_CLASS, GPT, MAIN_MENU, VICTOR = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("class_user"):
        return await main_menu(update, context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}\nВ каком классе ты учишься?",
    )
    return GET_CLASS


async def get_users_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    class_user = update.effective_message.text
    if class_user.isdigit():
        context.user_data["class_user"] = int(class_user)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Информация о тебе: {update.effective_user.full_name} {class_user}",
        )
        return await main_menu(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Неверный формат класса. Напиши только номер класса без букв",
        )
        return GET_CLASS


async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["Спросить у Ассистента"], ["Викторина"], ["/start"]]
    markup = ReplyKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери, что ты хочешь сделать?",
        reply_markup=markup,
    )
    return MAIN_MENU


async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Вы зашли в ассистента. Задайте вопрос?",
    )
    return GPT


async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m_text = update.effective_message.text
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions="Ты ассистент школьника, ты должен не давать точный ответ, а давать то, после чего школьник подумал и сам всё сделал.",
        input=m_text,
    )
    answer_text = response.output_text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer_text,
    )


async def victor_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите название темы, на которую вы хотите викторину.",
    )
    return VICTOR


async def victor_asver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tema = update.effective_message.text
    class_user = context.user_data.get("class_user")
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=f"Сделай викторину за {class_user} класс на тему, которую скажет пользователь",
        input=tema,
    )
    answer_text = response.output_text

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer_text,
    )


if __name__ == "__main__":
    persistence = PicklePersistence("bot_cache")
    application = (
        ApplicationBuilder().token(os.getenv("TOKEN")).persistence(persistence).build()
    )

    # Handler - обработчик
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_CLASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_users_class),
            ],
            MAIN_MENU: [
                MessageHandler(filters.Regex("Спросить у Ассистента"), start_gpt),
                MessageHandler(filters.Regex("Викторина"), victor_topic),
            ],
            GPT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt)],
            VICTOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, victor_asver)],
        },
        fallbacks=[CommandHandler("start", start)],  # то что будет всегда работать
        persistent=True,
        name="conv_hand",
    )

    application.add_handler(conv_handler)
    application.run_polling()
