import os
import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 10 ta islom mamlakati: (bayroq, nomi, shahar)
ISLAMIC_COUNTRIES = [
    ("🇸🇦", "Saudiya Arabistoni", "Riyadh"),
    ("🇵🇰", "Pakistan", "Islamabad"),
    ("🇮🇩", "Indoneziya", "Jakarta"),
    ("🇹🇷", "Turkiya", "Istanbul"),
    ("🇪🇬", "Misr", "Cairo"),
    ("🇺🇿", "Oʻzbekiston", "Tashkent"),
    ("🇲🇦", "Marokash", "Rabat"),
    ("🇮🇷", "Eron", "Tehran"),
    ("🇧🇩", "Bangladesh", "Dhaka"),
    ("🇦🇪", "BAA", "Dubai"),
]

# Namoz turlari va ularning rakat soni
NAMOZ_RAKATLAR = {
    "Fajr": "2 sunnat",
    "Dhuhr": "4 sunnat, 4 farz, 2 sunnat, 2 nafl",
    "Asr": "4 sunnat, 4 farz",
    "Maghrib": "3 farz, 2 sunnat, 2 nafl",
    "Isha": "4 sunnat, 4 farz, 2 sunnat, 2 nafl, 3 vitr"
}

# Mamlakatlar menyusini yaratish
def build_country_keyboard():
    buttons = []
    for i in range(0, len(ISLAMIC_COUNTRIES), 2):
        row = []
        flag1, name1, _ = ISLAMIC_COUNTRIES[i]
        row.append(InlineKeyboardButton(f"{flag1} {name1}", callback_data=f"prayer_{i}"))
        if i + 1 < len(ISLAMIC_COUNTRIES):
            flag2, name2, _ = ISLAMIC_COUNTRIES[i + 1]
            row.append(InlineKeyboardButton(f"{flag2} {name2}", callback_data=f"prayer_{i+1}"))
        buttons.append(row)
    return InlineKeyboardMarkup(buttons)

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi islom mamlakatlaridan birini tanlang:",
        reply_markup=build_country_keyboard()
    )

# Aladhan API orqali namoz vaqtlarini olish
def get_prayer_times(city):
    url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&method=2"
    response = requests.get(url, timeout=10)
    data = response.json()
    if data.get("code") != 200:
        raise Exception("Ma'lumot topilmadi")
    return data["data"]

# Tugma bosilganda ishlov berish
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Orqaga qaytish
    if query.data == "back_to_menu":
        await query.edit_message_text(
            "🌙 Quyidagi islom mamlakatlaridan birini tanlang:",
            reply_markup=build_country_keyboard()
        )
        return

    # Namoz vaqtlari so'rovi
    if query.data.startswith("prayer_"):
        try:
            index = int(query.data.split("_")[1])
            flag, country, city = ISLAMIC_COUNTRIES[index]
        except (IndexError, ValueError, IndexError):
            await query.edit_message_text("⚠️ Noto'g'ri tanlov.")
            return

        # Yuklanayotgani haqida xabar
        await query.edit_message_text("⏳ Ma'lumot yuklanmoqda... Iltimos, kuting.")

        try:
            prayer_data = get_prayer_times(city)
            timings = prayer_data["timings"]
            greg = prayer_data["date"]["gregorian"]
            hijri = prayer_data["date"]["hijri"]

            greg_date = f"{greg['day']} {greg['month']['en']} {greg['year']}"
            hijri_date = f"{hijri['day']} {hijri['month']['en']} {hijri['year']} (Hijriy)"

            message_text = (
                f"📍 **{flag} {country}** ({city})\n\n"
                f"📅 **Sana (Milodiy):** {greg_date}\n"
                f"📅 **Sana (Hijriy):** {hijri_date}\n\n"
                f"🕋 **Namoz vaqtlari:**\n"
                f"🔹 **Bomdod (Fajr):** {timings['Fajr']} — {NAMOZ_RAKATLAR['Fajr']}\n"
                f"🔹 **Peshin (Dhuhr):** {timings['Dhuhr']} — {NAMOZ_RAKATLAR['Dhuhr']}\n"
                f"🔹 **Asr:** {timings['Asr']} — {NAMOZ_RAKATLAR['Asr']}\n"
                f"🔹 **Shom (Maghrib):** {timings['Maghrib']} — {NAMOZ_RAKATLAR['Maghrib']}\n"
                f"🔹 **Xufton (Isha):** {timings['Isha']} — {NAMOZ_RAKATLAR['Isha']}\n\n"
                f"🌙 **Saharlik (Imsak):** {timings['Imsak']}\n"
                f"🍽️ **Iftorlik:** {timings['Maghrib']}"
            )

            # Yangilash va orqaga tugmalari
            refresh_button = InlineKeyboardButton("🔄 Yangilash", callback_data=f"prayer_{index}")
            back_button = InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")
            reply_markup = InlineKeyboardMarkup([[refresh_button, back_button]])

            await query.edit_message_text(message_text, parse_mode="Markdown", reply_markup=reply_markup)

        except Exception as e:
            logger.error(f"Xatolik: {e}")
            await query.edit_message_text(
                "❌ Namoz vaqtlarini olishda xatolik yuz berdi.\n\n"
                "Iltimos, keyinroq qaytadan urinib ko'ring.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_menu")]
                ])
            )

# Botni ishga tushirish
def main():
    TOKEN = os.environ["TOKEN"]
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
