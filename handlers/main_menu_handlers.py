from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ContextTypes,
)
from config.states import GET_CLASS, MAIN_MENU, SETTINGS
#from ..config.states import GET_CLASS, MAIN_MENU, SETTINGS
from db.users_crud import update_user

#--------------------------------------------------------
async def get_users_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    class_user = update.effective_message.text
    if class_user.isdigit():
        await update_user(update.effective_user.id, int(class_user))
        context.user_data["class_user"] = int(class_user)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Информация о тебе: {update.effective_user.full_name} {class_user} класс",
        )
        return await main_menu(update, context)
    else:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Неверный формат класса. Напиши только номер класса без букв",
        )
        return GET_CLASS
#----------------------------------------------------------------------------------------

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Спросить у Ассистента", callback_data='gpt_ask')],
        [InlineKeyboardButton("Викторина", callback_data='victor')],
        [InlineKeyboardButton("Настройки",callback_data='settings')],
        [InlineKeyboardButton("/start",callback_data='main_menu')],
    ]
    markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери, что ты хочешь сделать?",
        reply_markup=markup,
    )
    return MAIN_MENU

#-----------------------------------------------------------------------------
async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Вы зашли в настройки", show_alert=True)

    keyboard = [[InlineKeyboardButton("Поменять класс", callback_data="change_class")]]
    markup = InlineKeyboardMarkup(keyboard)
    class_user = update.effective_message.text
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Ваш класс: {class_user}",
        reply_markup=markup,
    )
    return SETTINGS

#-----------------------------------------------------------------------------------
async def change_class(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    await query.edit_message_text("Введите новый класс.")
    return GET_CLASS
