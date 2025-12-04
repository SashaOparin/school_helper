from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from openai import OpenAI

from config.states import GET_VICTOR_TOPIC, GET_VICTOR_ANSWER
import json
from handlers.main_menu_handlers import main_menu


# ---------------------------------------------------------------------------
async def victor_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Введите название темы, на которую вы хотите викторину.",
        reply_markup=markup,
    )

    return GET_VICTOR_TOPIC


async def victor_asver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tema = update.effective_message.text
    class_user = context.user_data.get("class_user")
    client = OpenAI()

    response = client.responses.create(
        model="gpt-4o-mini",
        instructions=f"Сделай викторину за {class_user} класс на тему, которую скажет пользователь. В викторине должно быть пять вопросов. Формат ответа должен быть следующий:"
        + '{"victorina":[{"question":"...", "answers":["...","...","...","..."]"correct_answer":".."}]}'
        + "\nНИЧЕГО КРОМЕ ЭТОГО НЕ ПИШИ",
        input=tema,
    )
    answer_text = response.output_text
    print(answer_text)
    victorina_dic = json.loads(answer_text)
    question_list = victorina_dic["victorina"]
    context.user_data["question_list"] = question_list
    context.user_data["num_quest"] = 0
    return await ask_question(update, context)


# -------------------------------------------------------------------------------
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    question_list = context.user_data["question_list"]
    question = question_list[context.user_data["num_quest"]]
    keyboard = []
    
    for answer in question["answers"]:
        row = [InlineKeyboardButton(answer, callback_data=answer)]
        
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)
    if query:
        await query.answer()
        await query.edit_message_text(text=question["question"], reply_markup=markup)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=question["question"], reply_markup=markup
        )
    return GET_VICTOR_ANSWER


async def get_ansver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    

    s_answer = query.data
    question_list = context.user_data["question_list"]
    print(context.user_data["num_quest"])
    current_question = question_list[context.user_data["num_quest"]]

    if s_answer == current_question["correct_answer"]:
        await query.answer("Правильный ответ")
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id, text=
        # )
    else:
        await query.answer("Неправильный ответ")
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id, text="Неправильный ответ"
        # )

    context.user_data["num_quest"] += 1
    if context.user_data["num_quest"] < len(question_list):
        return await ask_question(update, context)
    


# -----------------------------------------------------------
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await main_menu(update, context)
