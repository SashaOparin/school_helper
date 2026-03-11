from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from openai import AsyncOpenAI

from config.states import GPT
from handlers.main_menu_handlers import main_menu


# -----------------------------------------------------------------------
async def start_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Вы зашли в ассистента. Задайте вопрос?",
        reply_markup=markup,
    )
    return GPT


async def ask_gpt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_history = context.user_data.get("message_history", [])
    m_text = update.effective_message.text
    client = AsyncOpenAI()
    await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Ушёл за ответом, скоро вернусь "
        )
    if len(message_history) >= 6:
        message_history.pop(0)
        message_history.pop(0)
    response = await client.responses.create(
        model="gpt-5-mini",
        # instructions="Ты ассистент школьника, ты должен не давать точный ответ, а давать то, после чего школьник подумал и сам всё сделал.",
        input=[
            {
                "role": "developer",
                "content": f"Ты ассистент школьника {context.user_data['class_user']} класса, ты должен не давать точный ответ, а давать то, после чего школьник подумал и сам всё сделал.Если вопрос не требует от тебя решения к примеру задачи или написания сочинения и так дале, то можно ответить прямо и понятно,к примеру (cколько костей у человека),(что делать если ты потерялся в лесу) и т.д..В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ. ",
            },
            
        ]
        + message_history + [{"role": "user", "content": m_text}]
    )
    answer_text = response.output_text
    message_history.append({"role": "user", "content": m_text})
    message_history.append({"role": "assistant", "content": answer_text})
    context.user_data["message_history"] = message_history
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=answer_text, 
        reply_markup=markup,
    )


# --------------------------------------------
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await main_menu(update, context)
