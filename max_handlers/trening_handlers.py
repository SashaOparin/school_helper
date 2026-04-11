from openai import AsyncOpenAI

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback, MessageCreated
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from max_handlers.main_menu_handlers import build_back_menu
from max_handlers.max_states import MaxStates


# Вход в подготовку к контрольной
async def start_kontrol(event: MessageCallback, context: MemoryContext):
    await context.set_state(MaxStates.kontrol)
    await event.answer()
    await event.message.delete()
    await event.message.answer(
        text=(
            "Вы зашли в план подготовки к контрольной. "
            "Напиши предмет, тему и всё, что посчитаете нужным.\n"
            "Пример: биология, клетки"
        ),
        attachments=[build_back_menu()],
    )


# Генерируем вопросы и ответы для контрольной
async def hp_kontrol(event: MessageCreated, context: MemoryContext):
    m_text = (event.message.body.text or "").strip()
    data = await context.get_data()
    class_user = data.get("class_user", "")
    client = AsyncOpenAI()

    await event.message.answer("Создаю вопросы для контрольной")
    response = await client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "developer",
                "content": (
                    f"Ты ассистент школьника {class_user} класса, {m_text} вот тема и предмет по которому будет контрольная ученика."
                    "Cоставь достаточное количество вопросов ((старайся что бы их было как можно меньше,желательно около 20) НЕ ВТЫКАЙ 2 ВОПРОСА В 1),"
                    "что бы если он знал ответы на них с высокой долей вероятности получил 5 за контрольную."
                    "В ответе дай список вопросов в формате:вопрос1;вопрос2.НЕ ВКОЕМ СЛУЧАЕ НЕ ПИШИ ПУСТЫХ ПУНКТОВ. "
                    "Пиши только вопросы, ничего кроме них не пиши.В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ."
                ),
            },
        ],
    )

    question_text = response.output_text
    question_of_kontrol = question_text.split(";")

    text = "Вот вопросы для контрольной:\n"
    for i, question in enumerate(question_of_kontrol):
        text += f"{i + 1}. {question}\n"
    text += "\nНиже ответы по которым ты можешь себя проверить."

    await event.message.answer(text)

    await event.message.answer("Создаю ответы")
    response = await client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "developer",
                "content": (
                    f"Ты ассистент школьника {class_user} класса,дай ответы на эти вопросы: {question_text}."
                    "Пиши только ответы(СТАРАЙСЯ ЧТОБЫ БЫЛО ПОНЯТНО, НО КРАТКО), ничего кроме них не пиши."
                    "Ответы пиши в формате 1. ####, новая строка 2. #### и так далее."
                    "В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ.Пиши грамотно, без любых ошибок."
                ),
            },
        ],
    )

    answer_text = response.output_text
    await context.update_data(kontrol_answers=answer_text)
    await context.set_state(MaxStates.get_kontrol_answer)

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Показать ответы", payload="show_kontrol_answers"))
    builder.row(CallbackButton(text="Назад", payload="back"))

    await event.message.answer(
        text="Ответы готовы. Нажми кнопку, когда захочешь посмотреть.",
        attachments=[builder.as_markup()],
    )


# Показываем ответы только после нажатия кнопки
async def show_kontrol_answers(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()
    answer_text = data.get("kontrol_answers", "Ответы пока не готовы")

    await event.answer()
    await event.message.delete()
    await event.message.answer(
        text="Ответы по которым ты можешь себя проверить:\n" + answer_text,
        attachments=[build_back_menu()],
    )
