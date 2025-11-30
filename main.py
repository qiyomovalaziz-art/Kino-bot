import os
import logging
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Mamlakatlar: (bayroq, ko'rsatiladigan nom, shahar)
ISLAMIC_COUNTRIES = [
    ("🇸🇦", "Saudiya Arabistoni", "Riyadh"),
    ("🇵🇰", "Pakistan", "Islamabad"),
    ("🇮🇩", "Indoneziya", "Jakarta"),
    ("🇹🇷", "Turkiya", "Istanbul"),
    ("🇪🇬", "Misr", "Cairo"),
    ("🇺🇿", "O'zbekiston", "Tashkent"),
    ("🇲🇦", "Marokash", "Rabat"),
    ("🇮🇷", "Eron", "Tehran"),
    ("🇧🇩", "Bangladesh", "Dhaka"),
    ("🇦🇪", "BAA", "Dubai"),
]

# Shahar → Mamlakat kodi
COUNTRY_CODES = {
    "Riyadh": "SA",
    "Islamabad": "PK",
    "Jakarta": "ID",
    "Istanbul": "TR",
    "Cairo": "EG",
    "Tashkent": "UZ",
    "Rabat": "MA",
    "Tehran": "IR",
    "Dhaka": "BD",
    "Dubai": "AE",
}

# Namoz rakatlari
NAMOZ_RAKATLAR = {
    "Fajr": "2 sunnat",
    "Dhuhr": "4 sunnat, 4 farz, 2 sunnat, 2 nafl",
    "Asr": "4 sunnat, 4 farz",
    "Maghrib": "3 farz, 2 sunnat, 2 nafl",
    "Isha": "4 sunnat, 4 farz, 2 sunnat, 2 nafl, 3 vitr"
}

# Menyu tugmalari
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

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi islom mamlakatlaridan birini tanlang:",
        reply_markup=build_country_keyboard()
    )

# Namoz vaqtlarini olish (to'g'ri URL kodlangan)
def get_prayer_times(city):
    country_code = COUNTRY_CODES.get(city, "")
    encoded_city = urllib.parse.quote(city)
    url = f"http://api.aladhan.com/v1/timingsByCity?city={encoded_city}&country={country_code}&method=2"
    response = requests.get(url, timeout=12)
    data = response.json()
    if data.get("code") != 200:
        raise Exception(f"API xatosi: {data.get('status', 'Noma\'lum')}")
    return data["data"]

# Tugma bosilganda
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "back_to_menu":
        await query.edit_message_text(
            "🌙 Quyidagi islom mamlakatlaridan birini tanlang:",
            reply_markup=build_country_keyboard()
        )
        return

    if query.data.startswith("prayer_"):
        try:
            index = int(query.data.split("_")[1])
            flag, country, city = ISLAMIC_COUNTRIES[index]
        except (IndexError, ValueError):
            await query.edit_message_text("⚠️ Noto'g'ri tanlov.")
            return

        await query.edit_message_text("⏳ Ma'lumot yuklanmoqda... Iltimos, kuting.")

        try:
            prayer_data = get_prayer_times(city)
            t = prayer_data["timings"]
            g = prayer_data["date"]["gregorian"]
            h = prayer_data["date"]["hijri"]

            msg = (
                f"📍 **{flag} {country}** ({city})\n\n"
                f"📅 **Sana (Milodiy):** {g['day']} {g['month']['en']} {g['year']}\n"
                f"📅 **Sana (Hijriy):** {h['day']} {h['month']['en']} {h['year']} (Hijriy)\n\n"
                f"🕋 **Namoz vaqtlari:**\n"
                f"🔹 **Bomdod (Fajr):** {t['Fajr']} — {NAMOZ_RAKATLAR['Fajr']}\n"
                f"🔹 **Peshin (Dhuhr):** {t['Dhuhr']} — {NAMOZ_RAKATLAR['Dhuhr']}\n"
                f"🔹 **Asr:** {t['Asr']} — {NAMOZ_RAKATLAR['Asr']}\n"
                f"🔹 **Shom (Maghrib):** {t['Maghrib']} — {NAMOZ_RAKATLAR['Maghrib']}\n"
                f"🔹 **Xufton (Isha):** {t['Isha']} — {NAMOZ_RAKATLAR['Isha']}\n\n"
                f"🌙 **Saharlik (Imsak):** {t['Imsak']}\n"
                f"🍽️ **Iftorlik:** {t['Maghrib']}"
            )

            refresh = InlineKeyboardButton("🔄 Yangilash", callback_data=f"prayer_{index}")
            back = InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[refresh, back]]))

        except Exception as e:
            logger.error(f"Namoz vaqti xatosi: {e}")
            await query.edit_message_text(
                "❌ Namoz vaqtlarini olishda xatolik yuz berdi.\n\n"
                "Iltimos, keyinroq qaytadan urinib ko'ring.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Qayta urinish", callback_data=query.data)],
                    [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_menu")]
                ])
            )

# Asosiy ishga tushirish
def main():
    TOKEN = os.environ["TOKEN"]  # Railwaydan olinadi
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    logger.info("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
