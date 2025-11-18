# main.py
import os
import logging
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import sqlite3

# Log sozlamalari
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Sozlamalarni to'g'ridan-to'g'ri o'rnatish (GitHubga yuklaganda ehtimoliy xavfli!)
BOT_TOKEN = "8328030300:AAEfF3n6S1UVKttTqNGHY2GtPYqNKM2AOmE"
ADMIN_CHAT_ID = 7973934849  # Son sifatida — qavssiz!
DB_PATH = "kinolar.db"

# Ma'lumotlar bazasini yaratish
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kinolar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Kinoni saqlash
def saqla_kino(file_id: str, file_type: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO kinolar (file_id, file_type) VALUES (?, ?)", (file_id, file_type))
    kino_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return kino_id

# Kinoni ID bo'yicha olish
def olish_kino(kino_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT file_id, file_type FROM kinolar WHERE id = ?", (kino_id,))
    result = cursor.fetchone()
    conn.close()
    return result

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Salom! Kinoning **raqamini** yuboring — men uni ko'rsataman!\n"
        "Masalan: `123`"
    )

# Admin kino yuborganda
async def admin_kino_qabul(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        return  # Faqat admin

    message: Message = update.message
    file_id = None
    file_type = None

    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    else:
        await message.reply_text("⚠️ Faqat video, rasm yoki hujjat yuboring.")
        return

    if file_id:
        kino_id = saqla_kino(file_id, file_type)
        await message.reply_text(f"✅ Kino saqlandi!\nRaqami: `{kino_id}`", parse_mode="Markdown")

# Foydalanuvchi raqam yuborganda
async def raqamni_tekshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not text.isdigit():
        await update.message.reply_text("❌ Iltimos, faqat raqam yuboring (masalan: 123).")
        return

    kino_id = int(text)
    kino = olish_kino(kino_id)

    if kino:
        file_id, file_type = kino
        if file_type == "video":
            await update.message.reply_video(video=file_id)
        elif file_type == "photo":
            await update.message.reply_photo(photo=file_id)
        elif file_type == "document":
            await update.message.reply_document(document=file_id)
    else:
        await update.message.reply_text("❌ Bunday raqamli kino topilmadi.")

# Asosiy funksiya
def main():
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        raise ValueError("BOT_TOKEN va ADMIN_CHAT_ID sozlanmagan!")

    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.PHOTO | filters.Document.ALL,
        admin_kino_qabul
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, raqamni_tekshir))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == '__main__':
    main()
