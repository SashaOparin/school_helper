"""
Транскрипция голосовых сообщений через Whisper API.
"""
from pathlib import Path
import tempfile
from openai import AsyncOpenAI
from telegram import Update
from telegram.ext import ContextTypes


 
async def transcribe_voice(voice_path: Path) -> str:
    """Переводит голосовое в текст. voice_path — путь к ogg/м4а файлу."""
    client =  AsyncOpenAI()
    with open(voice_path, "rb") as f:
        resp = await client.audio.transcriptions.create(
            model="whisper-1",
            file=f,
        )
    return (resp.text or "").strip()

async def check_answer(question, answer) -> str:
    """"""
    client =  AsyncOpenAI()
    response = await client.responses.create(
        model="gpt-5-mini",
        instructions="Ты ассистент школьника, ты должен проверить ответ ученика на вопрос и сказать правильно он ответил или нет. Ответ должен быть в формате: 'Правильно' или 'Неправильно'",
        input=[
            {
                "role": "developer",
                "content": f"Вопрос: {question}\nОтвет ученика: {answer}",
            },
        ],
    )                                                                                                                                                                                                                                                                                    

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Голосовое сообщение — транскрибируем, парсим, сохраняем."""

    user_id = update.effective_user.id
    voice = update.message.voice
    if not voice:
        return

    await update.message.reply_text("Обрабатываю...")
    try:
        file = await context.bot.get_file(voice.file_id)
        tmp_path = Path(tempfile.mktemp(suffix=".ogg"))
        await file.download_to_drive(custom_path=tmp_path)
        try:
            text = await transcribe_voice(tmp_path)
        finally:
            tmp_path.unlink(missing_ok=True)

        if not text.strip():
            await update.message.reply_text("Не смог разобрать голос. Попробуй ещё раз.")
            return

        await update.message.reply_text(f"Распознал: {text}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")