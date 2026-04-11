from openai import AsyncOpenAI

from maxapi.context import MemoryContext
from maxapi.types import MessageCallback, MessageCreated

from max_handlers.main_menu_handlers import build_back_menu
from max_handlers.max_states import MaxStates


# Вход в GPT ассистента
async def start_gpt(event: MessageCallback, context: MemoryContext):
    await context.set_state(MaxStates.gpt)
    await event.answer()
    await event.message.delete()
    await event.message.answer(
        text="Вы зашли в ассистента. Задайте вопрос.",
        attachments=[build_back_menu()],
    )


# Ответ ассистента
async def ask_gpt(event: MessageCreated, context: MemoryContext):
    m_text = (event.message.body.text or "").strip()
    data = await context.get_data()
    message_history = data.get("message_history", [])
    client = AsyncOpenAI()

    # Ограничиваем историю, чтобы не росла бесконечно
    if len(message_history) >= 6:
        message_history.pop(0)
        message_history.pop(0)

    class_user = data.get("class_user", "")
    response = await client.responses.create(
        model="gpt-5-mini",
        input=[
            {
                "role": "developer",
                "content": (
                    f"Ты ассистент школьника {class_user} класса, "
                    "ты должен не давать точный ответ, а давать то, после чего "
                    "школьник подумал и сам всё сделал.Если вопрос не требует от "
                    "тебя решения к примеру задачи или написания сочинения и так "
                    "дале, то можно ответить прямо и понятно,к примеру (cколько "
                    "костей у человека),(что делать если ты потерялся в лесу) и т.д.."
                    "В ОТВЕТЕ НЕ БОЛЬШЕ ЧЕМ 1024 СИМВОЛОВ ПИШИ."
                ),
            },
        ]
        + message_history
        + [{"role": "user", "content": m_text}],
    )

    answer_text = response.output_text
    message_history.append({"role": "user", "content": m_text})
    message_history.append({"role": "assistant", "content": answer_text})
    await context.update_data(message_history=message_history)

    await event.message.answer(
        text=answer_text,
        attachments=[build_back_menu()],
    )
