from openai import AsyncOpenAI
from telegram import InlineKeyboardMarkup

# ===========================


from handlers.victorina_handlers import back
from telegram import (
    Update,
    InlineKeyboardButton,
)
from telegram.ext import (
    ContextTypes,
)

from config.states import KONTROL, GET_KONTROL_ANSWER
from handlers.main_menu_handlers import main_menu


async def start_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Вы зашли в план подготовки к контрольной. Напиши предмет,тему контрольной и всё что посчитаете нужным. \n Пример: Биология,Клетки",
        reply_markup=markup,
    )
    return KONTROL


async def hp_kontrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m_text = update.effective_message.text
    topic_predmet_kontrol = m_text
    # Здесь уже делаешь запрос в гпт.
    client = AsyncOpenAI()
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Создаю вопросы для контрольной."
    )
    response = await client.responses.create(
        model="gpt-5-mini",
        # instructions="Ты ассистент школьника, ты должен не давать точный ответ, а давать то, после чего школьник подумал и сам всё сделал.",
        input=[
            {
                "role": "developer",
                "content": f"Ты ассистент школьника {context.user_data['class_user']} класса, {topic_predmet_kontrol} вот тема и предмет по которому будет контрольная ученика."
                           f'Cоставь достаточное количество вопросов ((старайся что бы их было как можно меньше,желательно около 20) НЕ ВТЫКАЙ 2 ВОПРОСА В 1),что бы если он знал ответы на них с высокой долей вероятности получил 5 за контрольную.'
                           f'В ответе дай список вопросов в формате:вопрос1;вопрос2. Пиши только вопросы, ничего кроме них не пиши.В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ.',
            },
        ],
    )
    answer_text = response.output_text
    question_of_kontrol = answer_text.split(";")
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    print(question_of_kontrol, "вот вопросы для контрольной")
    text = "Вот вопросы для контрольной:\n"
    for i , question in enumerate (question_of_kontrol):
        text += f"{i+1}. {question}\n"

    text += "\nНиже ответы по которым ты можешь себя проверить."
# <tg-spoiler>Скрытый</tg-spoiler>
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup,
    )
    #-----------------
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="Создаю ответы."
    )
    response = await client.responses.create(
        model="gpt-5-mini",
        # instructions="Ты ассистент школьника, ты должен не давать точный ответ, а давать то, после чего школьник подумал и сам всё сделал.",
        input=[
            {
                "role": "developer",
                "content": f"Ты ассистент школьника {context.user_data['class_user']} класса,дай ответы на эти вопросы: {answer_text}."
                           f' Пиши только ответы(СТАРАЙСЯ ЧТОБЫ БЫЛО ПОНЯТНО, НО КРАТКО), ничего кроме них не пиши.Ответы пиши в формате 1. ####, новая строка 2. #### и так далее, номер 1 вопроса не пиши но сам текс пиши.'
                           f'В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ.НЕ ИСПОЛЬЗУЙ НИКАКИХ ЗНАКОВ ПРИПИНАНИЯ,КРОМЕ НОВОЙ СТРОКИ И ТОЧКИ ПОСЛЕ НОМЕРА ВОПРОСА.Но пиши грамотно, без любых ошибок.'
                           f'НЕ ИСПОЛЬЗУЙ НИКАКИХ ЗНАКОВ ПРИПИНАНИЯ,КРОМЕ НОВОЙ СТРОКИ.'
                           f'Ответы должны быть оформлены в скрытом формате, например: <tg-spoiler>текст ответа</tg-spoiler>.',
                           #f'ТЕКСТ ОТВЕТА ПОСТАВЬ ВОТ ТАК ||####|| , ОБЯЗАТЕЛЬНО ОБЕРНИ ТЕКС В ЭТИ 2 ПАЛКИ.',
            },
        ],
    )
    answer_text = response.output_text
    question_of_kontrol = answer_text.split(";")
    keyboard = [
        [InlineKeyboardButton("Назад", callback_data="back")],
    ]
    markup = InlineKeyboardMarkup(keyboard)
    
    print(question_of_kontrol)
    text = "Вот ответы по которым ты можешь себя проверить:\n"
    for i , question in enumerate (question_of_kontrol):
#         # text += f"{i + 1}. <tg-spoiler>{question}</tg-spoiler>"#n"
        text += f"{i+1}. {question}"
# ###text += f"{i + 1}. <tg-spoiler>{question} {i + 1}</tg-spoiler>"#n" пока это самый рабочий вариант 
# # <tg-spoiler>Скрытый</tg-spoiler>
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=markup,
        parse_mode="HTML",
    )   
    return GET_KONTROL_ANSWER


async def handle_text_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m_text = update.effective_message.text





# =========================================================
async def back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    return await main_menu(update, context)
