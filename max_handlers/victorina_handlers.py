import json

from openai import AsyncOpenAI

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback, MessageCreated
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from db.victorina_crud import create_victorina, get_victorina
from max_handlers.main_menu_handlers import build_back_menu, send_main_menu
from max_handlers.max_states import MaxStates

max_bot = None


# Передаем объект бота из main_max.py
def set_bot(bot):
    global max_bot
    max_bot = bot


# Вход в викторину
async def victor_topic(event: MessageCallback, context: MemoryContext):
    await context.set_state(MaxStates.get_victor_topic)
    await event.answer()
    await event.message.delete()
    await event.message.answer(
        text="Введите название темы для викторины",
        attachments=[build_back_menu()],
    )


# Генерируем или достаем викторину из БД
async def victor_answer(event: MessageCreated, context: MemoryContext):
    tema = (event.message.body.text or "").strip()
    data = await context.get_data()
    class_user = data.get("class_user")
    client = AsyncOpenAI()

    await event.message.answer("Придумываю викторину 😉")

    question_list = await get_victorina(class_num=class_user, topic=tema)

    if not question_list:
        response = await client.responses.create(
            model="gpt-5-mini",
            instructions=(
                f"Сделай викторину за {class_user} класс на тему, которую скажет пользователь. "
                "В викторине должно быть пять вопросов.Ответы должны быть не более 32 символов. "
                "Формат ответа должен быть следующий:"
                + '{"victorina":[{"question":"...", "answers":["...","...","...","..."], "correct_answer":".."}]}'
                + "\nНИЧЕГО КРОМЕ ЭТОГО НЕ ПИШИ"
            ),
            input=tema,
        )
        answer_text = response.output_text
        victorina_dic = json.loads(answer_text)
        question_list = victorina_dic["victorina"]
        await create_victorina(class_num=class_user, topic=tema, question_list=question_list)

    await context.update_data(question_list=question_list, num_quest=0, win=0, last_result_mid=None)
    await context.set_state(MaxStates.get_victor_answer)
    await ask_question(event.message, context)


# Отправляем текущий вопрос викторины
async def ask_question(message, context: MemoryContext):
    data = await context.get_data()
    question_list = data["question_list"]
    num_quest = data["num_quest"]
    question = question_list[num_quest]

    builder = InlineKeyboardBuilder()
    for answer in question["answers"]:
        builder.row(CallbackButton(text=answer, payload=f"victor_answer:{answer}"))

    await message.answer(
        text=question["question"],
        attachments=[builder.as_markup()],
    )


# Проверяем ответ викторины
async def get_answer(event: MessageCallback, context: MemoryContext):
    payload = event.callback.payload or ""
    selected_answer = payload.replace("victor_answer:", "", 1)

    data = await context.get_data()
    question_list = data["question_list"]
    num_quest = data["num_quest"]
    win = data.get("win", 0)
    last_result_mid = data.get("last_result_mid")
    current_question = question_list[num_quest]
    current_mid = event.message.body.mid

    await event.answer()

    # Удаляем прошлое сообщение "Правильный/Неправильный", как в TG-версии
    if last_result_mid:
        await max_bot.delete_message(message_id=last_result_mid)

    result_text = "Неправильный ответ"
    if selected_answer == current_question["correct_answer"]:
        win += 1
        result_text = "Правильный ответ"

    num_quest += 1

    if num_quest < len(question_list):
        # Убираем старые кнопки у уже отвеченного вопроса
        await event.message.edit(result_text, attachments=[])
        await context.update_data(num_quest=num_quest, win=win, last_result_mid=current_mid)
        await ask_question(event.message, context)
        return

    await event.message.edit(text=f"Количество правильных ответов - {win}/5", attachments=[])
    await context.update_data(last_result_mid=None)
    await send_main_menu(event.message, context)
