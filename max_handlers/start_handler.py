from maxapi.context import MemoryContext
from maxapi.types import MessageCreated

from db.users_crud import create_user, get_user
from max_handlers.main_menu_handlers import send_main_menu
from max_handlers.max_states import MaxStates


# /start — логика полностью как в телеге
async def start(event: MessageCreated, context: MemoryContext):
    user_id = event.message.sender.user_id
    username = event.message.sender.username
    first_name = event.message.sender.first_name

    user = await get_user(user_id)
    if not user:
        await create_user(user_id, username)
        user = await get_user(user_id)

    if user and user.get("class"):
        await context.update_data(class_user=user["class"])
        await send_main_menu(event.message, context)
        return

    await context.set_state(MaxStates.get_class)
    await event.message.answer(
        text=f"Привет, {first_name}\nВ каком классе ты учишься?"
    )
