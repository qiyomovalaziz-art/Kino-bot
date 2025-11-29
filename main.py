import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)
import requests
from datetime import datetime

# Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Holatlar
ASK_CITY = 1

# Namoz turlari uchun rakatlar
NAMOZ_RAKATLAR = {
    "Fajr": "2 sunnat",
    "Dhuhr": "4 sunnat, 4 farz, 2 sunnat, 2 nafl",
    "Asr": "4 sunnat, 4 farz",
    "Maghrib": "3 farz, 2 sunnat, 2 nafl",
    "Isha": "4 sunnat, 4 farz, 2 sunnat, 2 nafl, 3 vitr"
}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🕋 Namoz vaqtlarini ko'rsat", callback_data='show_prayer')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Assalomu alaykum! 🌙\nNamoz vaqtlari, sanasi, sovat vaqtlari hamda har bir namozning necha rakat ekanligini bilish uchun tugmani bosing:",
        reply_markup=reply_markup
    )

# Callback tugmalar
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'show_prayer':
        await query.edit_message_text("Shahringizni yoki mamlakatingizni kiriting (masalan: Toshkent, Jidda, Istanbul):")
        return ASK_CITY

# Shahar nomini qabul qilish
async def get_city(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = update.message.text.strip()
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country=&method=2"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data['code'] != 200 or 'data' not in data:
            await update.message.reply_text("Kechirasiz, ushbu shahar topilmadi. Iltimos, to'g'ri shahar nomini kiriting.")
            return ASK_CITY

        timings = data['data']['timings']
        date_info = data['data']['date']['gregorian']
        hijri = data['data']['date']['hijri']

        # Sana
        greg_date = f"{date_info['day']} {date_info['month']['en']} {date_info['year']}"
        hijri_date = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} (Hijriy)"

        # Iftorlik va Saharlik
        saharlik = timings['Imsak']
        iftorlik = timings['Maghrib']

        # Ma'lumotlarni tuzish
        message = (
            f"📅 **Sana (Milodiy):** {greg_date}\n"
            f"📅 **Sana (Hijriy):** {hijri_date}\n\n"
            f"🕋 **Namoz vaqtlari:**\n"
            f"🔹 **Bomdod (Fajr):** {timings['Fajr']} — {NAMOZ_RAKATLAR['Fajr']}\n"
            f"🔹 **Peshin (Dhuhr):** {timings['Dhuhr']} — {NAMOZ_RAKATLAR['Dhuhr']}\n"
            f"🔹 **Asr:** {timings['Asr']} — {NAMOZ_RAKATLAR['Asr']}\n"
            f"🔹 **Shom (Maghrib):** {timings['Maghrib']} — {NAMOZ_RAKATLAR['Maghrib']}\n"
            f"🔹 **Xufton (Isha):** {timings['Isha']} — {NAMOZ_RAKATLAR['Isha']}\n\n"
            f"🌙 **Saharlik (Imsak):** {saharlik}\n"
            f"🍽️ **Iftorlik:** {iftorlik}\n\n"
            f"📍 **Shahar:** {city}"
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await update.message.reply_text("Namoz vaqtlarini olishda xatolik yuz berdi. Iltimos, keyinroq qaytadan urinib ko'ring.")

    return ConversationHandler.END

# Bekor qilish
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Jarayon bekor qilindi.")
    return ConversationHandler.END

# Asosiy funksiya
def main():
    # 🔑 Bu yerga o'zingizning bot tokeningizni qo'ying
    TOKEN = "8581071094:AAF7qK3vVOn8YUJTrlc-JEGPX3SXw5wJMoA"

    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler)],
        states={
            ASK_CITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_city)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        per_chat=True
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)

    print("Bot ishga tushdi...")
    app.run_polling()

if __name__ == '__main__':
    main()
