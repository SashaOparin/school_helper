from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from openai import AsyncOpenAI

from config.states import GET_VICTOR_TOPIC, GET_VICTOR_ANSWER
import json
from db.victorina_crud import create_victorina, get_victorina
from handlers.main_menu_handlers import main_menu


# ---------------------------------------------------------------------------
async def victor_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Введите название темы, на которую вы хотите викторину.",
        reply_markup=markup,
    )

    return GET_VICTOR_TOPIC


async def victor_asver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tema = update.effective_message.text
    class_user = context.user_data.get("class_user")
    message = await context.bot.send_message(
            chat_id=update.effective_chat.id, text="Придумываю викторину 😉"
        )
    #пытаемся взять викторину из БД
    question_list = await get_victorina(class_num=class_user, topic=tema)
    print(question_list)

    # готовим викторину к задаванию вопросов
    if 'last_quest_id' in context.user_data:
        context.user_data.pop('last_quest_id')
    context.user_data['win'] = 0

    if not question_list:
        client = AsyncOpenAI()
        response = await client.responses.create(
            model="gpt-5-mini",
            instructions=f"Сделай викторину за {class_user} класс на тему, которую скажет пользователь. В викторине должно быть пять вопросов.Ответы должны быть не более 32 символов. Формат ответа должен быть следующий:"
            + '{"victorina":[{"question":"...", "answers":["...","...","...","..."], "correct_answer":".."}]}'
            + "\nНИЧЕГО КРОМЕ ЭТОГО НЕ ПИШИ",
            input=tema,
        )
        answer_text = response.output_text
        print(answer_text)
        victorina_dic = json.loads(answer_text)
        question_list = victorina_dic["victorina"]
        await create_victorina(class_num=class_user, topic=tema, question_list=question_list)
    
    # одинаковые действия для БД и ГПТ
    context.user_data["question_list"] = question_list
    context.user_data["num_quest"] = 0
    await context.bot.delete_message(chat_id = update.effective_chat.id, message_id = message.id)
    return await ask_question(update, context)


# -------------------------------------------------------------------------------
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    
    question_list = context.user_data["question_list"]
    question = question_list[context.user_data["num_quest"]]
    keyboard = []
    
    for answer in question["answers"]:
        row = [InlineKeyboardButton(answer, callback_data=answer + '.')]
        
        keyboard.append(row)
    markup = InlineKeyboardMarkup(keyboard)
    
    message = await context.bot.send_message(
        chat_id=update.effective_chat.id, text=question["question"], reply_markup=markup
    )
    
    return GET_VICTOR_ANSWER


async def get_ansver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    query = update.callback_query
    context.user_data['win'] = context.user_data.get('win', 0)  


    last_quest_id = context.user_data.get('last_quest_id')
    if last_quest_id: 
        await context.bot.delete_message(chat_id = update.effective_chat.id, message_id=last_quest_id)

    s_answer = query.data
    question_list = context.user_data["question_list"] 
    current_question = question_list[context.user_data["num_quest"]]
      
    if s_answer[:-1] == current_question["correct_answer"]:
        
        await query.edit_message_text("Правильный ответ")
        context.user_data['win'] += 1
        # await context.bot.send_message(
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        markup = InlineKeyboardMarkup(keyboard)        
        #     chat_id=update.effective_chat.id, text=
        # )
    else:
        await query.edit_message_text("Неправильный ответ")
        keyboard = [
            [InlineKeyboardButton("Назад", callback_data="back")],
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
    
        # await context.bot.send_message(
        #     chat_id=update.effective_chat.id, text="Неправильный ответ"
        # )

    context.user_data["num_quest"] += 1
    context.user_data['last_quest_id'] = query.message.id
    if context.user_data["num_quest"] < len(question_list):
        return await ask_question(update, context)
    else:
        await query.edit_message_text(
            text=f"Количество правильных ответов - {context.user_data['win']}/5 ",
        )

        return await main_menu(update, context) 




    


# -----------------------------------------------------------
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await main_menu(update, context)
