# main.py
import logging
import secrets
from telegram import Update, Message
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_CHAT_ID
from database import init_db, saqla_kino, olish_kino

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Bot ishga tushganda DB ni yaratish
init_db()

# /start buyrug'i
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎬 Salom! Kinoning kodini yuboring — men uni sizga ko'rsataman!\n"
        "Masalan: `KINO123`"
    )

# Admin kinoni yuborganda
async def admin_kino_qabul_qil(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_CHAT_ID:
        return  # Faqat admin

    message: Message = update.message
    kod = secrets.token_urlsafe(6).upper()[:6]  # 6 ta tasodifiy harf/raqam, masalan: A3B9K1

    file_id = None
    file_type = None

    if message.video:
        file_id = message.video.file_id
        file_type = "video"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
    elif message.photo:
        # Eng yuqori sifatli rasm
        file_id = message.photo[-1].file_id
        file_type = "photo"
    else:
        await message.reply_text("⚠️ Faqat video, foto yoki fayl yuboring.")
        return

    if file_id:
        saqla_kino(kod, file_id, file_type)
        await message.reply_text(f"✅ Kino saqlandi!\nKod: `{kod}`", parse_mode="Markdown")

# Foydalanuvchi kod yuborganda
async def kodni_tekshir(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().upper()
    
    # Kod 3-10 ta harf/raqamdan iborat bo'lishi mumkin
    if not (3 <= len(text) <= 10) or not text.isalnum():
        await update.message.reply_text("❌ Kod noto'g'ri. Iltimos, to'g'ri kod yuboring.")
        return

    kino = olish_kino(text)
    if kino:
        file_id, file_type = kino
        if file_type == "video":
            await update.message.reply_video(video=file_id)
        elif file_type == "photo":
            await update.message.reply_photo(photo=file_id)
        elif file_type == "document":
            await update.message.reply_document(document=file_id)
    else:
        await update.message.reply_text("❌ Bunday kodli kino topilmadi.")

# Asosiy funksiya
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.VIDEO | filters.PHOTO | filters.Document.ALL,
        admin_kino_qabul_qil
    ))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, kodni_tekshir))

    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == '__main__':
    main()
