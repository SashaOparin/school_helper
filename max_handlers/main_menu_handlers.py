from maxapi.context import MemoryContext
from maxapi.types import MessageCallback, MessageCreated
from maxapi.types.attachments.buttons import CallbackButton
from maxapi.utils.inline_keyboard import InlineKeyboardBuilder

from db.users_crud import update_user
from max_handlers.max_states import MaxStates


# Сборка главного меню
def build_main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Поменять класс", payload="settings"))
    builder.row(CallbackButton(text="Спросить у Ассистента", payload="gpt_ask"))
    builder.row(CallbackButton(text="Викторина", payload="victor"))
    builder.row(CallbackButton(text="Подготовиться к контрольной", payload="kontrol"))
    return builder.as_markup()


# Сборка кнопки назад
def build_back_menu():
    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Назад", payload="back"))
    return builder.as_markup()


# Универсальный вход в главное меню
async def send_main_menu(message, context: MemoryContext):
    await context.set_state(MaxStates.main_menu)
    await message.answer(
        text="Выберите, что вы хотите сделать",
        attachments=[build_main_menu()],
    )


# Шаг выбора класса
async def get_users_class(event: MessageCreated, context: MemoryContext):
    class_user = (event.message.body.text or "").strip()
    user_id = event.message.sender.user_id

    if class_user.isdigit() and int(class_user) <= 11:
        class_num = int(class_user)
        await update_user(user_id, class_num)
        await context.update_data(class_user=class_num)

        await event.message.answer(
            text=f"Информация о тебе: {event.message.sender.first_name} {class_num} класс"
        )
        await send_main_menu(event.message, context)
        return

    await event.message.answer(
        text="Неверный формат класса. Напиши только номер класса без букв или нет такого класса."
    )


# Меню настройки класса
async def settings(event: MessageCallback, context: MemoryContext):
    data = await context.get_data()
    class_user = data.get("class_user", "не указан")

    await context.set_state(MaxStates.settings)
    await event.answer()
    await event.message.delete()

    builder = InlineKeyboardBuilder()
    builder.row(CallbackButton(text="Поменять класс", payload="change_class"))
    builder.row(CallbackButton(text="Назад", payload="back"))

    await event.message.answer(
        text=f"Ваш класс: {class_user}",
        attachments=[builder.as_markup()],
    )


# Переход к вводу нового класса
async def change_class(event: MessageCallback, context: MemoryContext):
    await context.set_state(MaxStates.get_class)
    await event.answer()
    await event.message.delete()
    await event.message.answer("Введите новый класс")


# Кнопка назад должна работать из всех веток
async def back(event: MessageCallback, context: MemoryContext):
    await event.answer()
    await event.message.delete()
    await send_main_menu(event.message, context)
