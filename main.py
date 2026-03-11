import logging
import os
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    PicklePersistence,
    CallbackQueryHandler,
)

# ===========================
from dotenv import load_dotenv

from handlers.main_menu_handlers import settings, get_users_class, change_class

from handlers.start_handler import start

from handlers.gpt_handlers import start_gpt, ask_gpt

from handlers.victorina_handlers import victor_asver, victor_topic, back, get_ansver

from handlers.trening_handlers import start_kontrol,hp_kontrol, handle_text_answer
# from handlers.whisper import handle_voice_answer

from config.states import (
    GET_CLASS,
    GPT,
    MAIN_MENU,
    GET_VICTOR_TOPIC,
    SETTINGS,
    GET_VICTOR_ANSWER,
    KONTROL,
    GET_KONTROL_ANSWER
)
from db.database import create_tables
from handlers.whisper import transcribe_voice

# =====================================================================
load_dotenv()

# логирование
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
# ------------------------------------------------------------------------

if __name__ == "__main__":
    persistence = PicklePersistence("bot_cache")
    application = (
        ApplicationBuilder()
        .token(os.getenv("TOKEN"))
        .post_init(create_tables)
        .persistence(persistence)
        .build()
    )

    # Handler - обработчик
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_CLASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_users_class),
            ],
            MAIN_MENU: [
                MessageHandler(filters.Regex("Настройки"), settings),
                CallbackQueryHandler(start_gpt, pattern="gpt_ask"),
                CallbackQueryHandler(victor_topic, pattern="victor"),
                CallbackQueryHandler(settings, pattern="settings"),
                CallbackQueryHandler(start_kontrol, pattern="kontrol"),
            ],
            GPT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, ask_gpt),
                CallbackQueryHandler(back, pattern="back"),
            ],
            GET_VICTOR_TOPIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, victor_asver),
                CallbackQueryHandler(back, pattern="back"),
            ],
            GET_VICTOR_ANSWER: [
                CallbackQueryHandler(get_ansver),  # кнопчки
            ],
            SETTINGS: [
                CallbackQueryHandler(change_class, pattern="change_class"),
                CallbackQueryHandler(back, pattern="back"),
            ],
            KONTROL: [
                CallbackQueryHandler(back, pattern="back"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, hp_kontrol),
            ],
            GET_KONTROL_ANSWER:[
                MessageHandler(filters.VOICE, transcribe_voice), 
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_answer)
            ]
        },
        fallbacks=[CommandHandler("start", start)],  # то что будет всегда работать
        persistent=True,
        name="conv_hand",
    )
    application.add_handler(conv_handler)
    application.run_polling()
