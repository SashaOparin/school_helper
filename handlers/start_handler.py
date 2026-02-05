from telegram import (
    Update,
)
from telegram.ext import (
    ContextTypes,
)

from config.states import GET_CLASS
from handlers.main_menu_handlers import main_menu
from db.users_crud import create_user, get_user


# ---------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = await get_user(update.effective_user.id)
    if not user:
        await create_user(update.effective_user.id, update.effective_user.username)
        user = await get_user(update.effective_user.id)   

    await update.message.delete()
    if context.user_data.get("class_user") or user["class"]:
        context.user_data["class_user"] = user["class"]
        return await main_menu(update, context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}\nВ каком классе ты учишься?",
    )
    
    return GET_CLASS
