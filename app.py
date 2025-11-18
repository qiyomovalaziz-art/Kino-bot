import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    CallbackQueryHandler
)
from database import init_db, add_user, get_user_count, add_movie, get_movie_by_code

# === Sozlamalar ===
BOT_TOKEN = "8328030300:AAEfF3n6S1UVKttTqNGHY2GtPYqNKM2AOmE"
ADMIN_ID = 7973934849

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Boshlang'ich sozlamalar ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username)
    await update.message.reply_text(
        "Assalomu alaykum! 🎬\n"
        "Kinoni ko'rish uchun uning *raqamli kodini* yuboring.",
        parse_mode='Markdown'
    )

# === Admin panel ===
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("Siz admin emassiz!")
        return

    keyboard = [
        [InlineKeyboardButton("➕ Kino qo'shish", callback_data='add_movie')],
        [InlineKeyboardButton("📊 Statistika", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Admin panel:", reply_markup=reply_markup)

# === Callbacklar ===
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'add_movie':
        context.user_data['state'] = 'waiting_for_code'
        await query.edit_message_text("Kino uchun *raqamli kod*ni yuboring:", parse_mode='Markdown')

    elif query.data == 'stats':
        count = get_user_count()
        await query.edit_message_text(f"👥 Botdan foydalanuvchilar soni: {count}")

# === Xabarlar ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    # Foydalanuvchi kino kodini yubordi
    if not context.user_data.get('state') and not text.startswith('/'):
        movie = get_movie_by_code(text)
        if movie:
            file_id, title = movie
            await update.message.reply_video(file_id, caption=f"🎬 *{title}*", parse_mode='Markdown')
        else:
            await update.message.reply_text("⚠️ Bunday kodli kino topilmadi. Iltimos, to'g'ri kodni kiriting.")
        return

    # Admin kino qo'shish jarayoni
    if user_id == ADMIN_ID:
        state = context.user_data.get('state')

        if state == 'waiting_for_code':
            if not text.isdigit():
                await update.message.reply_text("⚠️ Kod faqat raqamlardan iborat bo'lishi kerak!")
                return
            context.user_data['code'] = text
            context.user_data['state'] = 'waiting_for_title'
            await update.message.reply_text("Kino nomini yuboring:")

        elif state == 'waiting_for_title':
            context.user_data['title'] = text
            context.user_data['state'] = 'waiting_for_file'
            await update.message.reply_text("Endi kinoning *video faylini* yuboring:", parse_mode='Markdown')

        elif state == 'waiting_for_file':
            if not update.message.video:
                await update.message.reply_text("⚠️ Iltimos, faqat *video* yuboring!", parse_mode='Markdown')
                return

            code = context.user_data['code']
            title = context.user_data['title']
            file_id = update.message.video.file_id

            try:
                add_movie(code, title, file_id)
                await update.message.reply_text(f"✅ Kino muvaffaqiyatli qo'shildi!\nKod: `{code}`", parse_mode='Markdown')
            except Exception as e:
                await update.message.reply_text(f"❌ Xatolik yuz berdi: {e}")
            finally:
                context.user_data.clear()

# === Asosiy funksiya ===
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_panel))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()
