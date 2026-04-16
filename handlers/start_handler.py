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
async def start(update: Update, context: ConteООООffective_user.id)   

    await update.message.delete()
    if context.user_data.get("class_user") or user["class"]:
        context.user_data["class_user"] = user["class"]
        return await main_menu(update, context)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Привет, {update.effective_user.first_name}\nВ каком классе ты учишься?",
    )J


    6J6
    ';ORA1df'
    
    return GET_CLASS
