# main.py
import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from database import init_db, olish_kino

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN", "8328030300:AAEfF3n6S1UVKttTqNGHY2GtPYqNKM2AOmE")

init_db()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Kinoning raqamini yuboring!\nMasalan: `123`"
    )

async def kodni_tekshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    if not text.isdigit():
        await update.message.reply_text("❌ Faqat raqam yuboring.")
        return

    kino = olish_kino(int(text))
    if not kino:
        await update.message.reply_text("❌ Kino topilmadi.")
        return

    file_id, file_type = kino
    if file_type == "video":
        await update.message.reply_video(video=file_id)
    elif file_type == "photo":
        await update.message.reply_photo(photo=file_id)
    elif file_type == "document":
        await update.message.reply_document(document=file_id)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kodni_tekshir))
    app.run_polling()

if __name__ == "__main__":
    main()
