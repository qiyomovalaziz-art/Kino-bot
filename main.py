import os
import logging
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Mamlakatlar: (bayroq, ko'rsatiladigan nom, API uchun shahar nomi)
ISLAMIC_COUNTRIES = [
    ("🇸🇦", "Saudiya Arabistoni", "Riyadh"),
    ("🇵🇰", "Pakistan", "Karachi"),
    ("🇮🇩", "Indoneziya", "Jakarta"),
    ("🇹🇷", "Turkiya", "Istanbul"),
    ("🇪🇬", "Misr", "Cairo"),
    ("🇺🇿", "O'zbekiston", "Tashkent"),
    ("🇲🇦", "Marokash", "Casablanca"),
    ("🇮🇷", "Eron", "Tehran"),
    ("🇧🇩", "Bangladesh", "Dhaka"),
    ("🇦🇪", "BAA", "Dubai"),
]

# Namoz rakatlari (o'zgarmaydi)
NAMOZ_RAKATLAR = {
    "Fajr": "2 sunnat",
    "Dhuhr": "4 sunnat, 4 farz, 2 sunnat, 2 nafl",
    "Asr": "4 sunnat, 4 farz",
    "Maghrib": "3 farz, 2 sunnat, 2 nafl",
    "Isha": "4 sunnat, 4 farz, 2 sunnat, 2 nafl, 3 vitr"
}

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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi islom mamlakatlaridan birini tanlang:",
        reply_markup=build_country_keyboard()
    )

# YANGI: Yangi API orqali namoz vaqtlarini olish
def get_prayer_times_new(city):
    # Shahar nomini URLga mos qilish
    encoded_city = urllib.parse.quote(city)
    url = f"https://islamic-api.vercel.app/api/jadwalSholat?daerah={encoded_city}"
    response = requests.get(url, timeout=10)
    data = response.json()
    
    if not data.get("status"):
        raise Exception("Shahar topilmadi")
    
    jadwal = data["data"]
    # Sana (bugungi)
    from datetime import datetime
    today = datetime.now()
    greg_date = today.strftime("%d %B %Y")
    hijri_date = "Hijriy sana API tomonidan qo'llab-quvvatlanmaydi"
    
    # Namoz vaqtlarini moslashtirish
    timings = {
        "Fajr": jadwal["subuh"],      # Subuh = Fajr
        "Dhuhr": jadwal["dzuhur"],
        "Asr": jadwal["ashar"],
        "Maghrib": jadwal["maghrib"],
        "Isha": jadwal["isya"],
        "Imsak": jadwal["imsak"]
    }
    
    return {
        "timings": timings,
        "date": {
            "gregorian": {
                "day": today.strftime("%d"),
                "month": {"en": today.strftime("%B")},
                "year": today.strftime("%Y")
            },
            "hijri": {
                "day": "?",
                "month": {"en": "?"},
                "year": "?"
            }
        }
    }

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
            prayer_data = get_prayer_times_new(city)
            t = prayer_data["timings"]
            g = prayer_data["date"]["gregorian"]
            h_day = prayer_data["date"]["hijri"]["day"]

            msg = (
                f"📍 **{flag} {country}** ({city})\n\n"
                f"📅 **Sana (Milodiy):** {g['day']} {g['month']['en']} {g['year']}\n"
                f"📅 **Sana (Hijriy):** —\n\n"
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
            logger.error(f"Yangi API xatosi: {e}")
            await query.edit_message_text(
                "❌ Namoz vaqtlarini olishda xatolik yuz berdi.\n\n"
                "Iltimos, keyinroq qaytadan urinib ko'ring.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("🔄 Qayta urinish", callback_data=query.data)],
                    [InlineKeyboardButton("🏠 Bosh menyu", callback_data="back_to_menu")]
                ])
            )

def main():
    TOKEN = os.environ["TOKEN"]
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    logger.info("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
