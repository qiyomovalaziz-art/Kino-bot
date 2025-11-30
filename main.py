import os
import logging
import requests
import urllib.parse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    await update.message.reply_text("🌙 Assalomu alaykum! Quyidagi islom mamlakatlaridan birini tanlang:", reply_markup=build_country_keyboard())

def get_prayer_times_new(city):
    encoded_city = urllib.parse.quote(city)
    url = f"https://islamic-api.vercel.app/api/jadwalSholat?daerah={encoded_city}"
    response = requests.get(url, timeout=10)
    data = response.json()
    if not data.get("status"):
        raise Exception("Shahar topilmadi")
    j = data["data"]
    from datetime import datetime
    today = datetime.now()
    return {
        "timings": {
            "Fajr": j["subuh"],
            "Dhuhr": j["dzuhur"],
            "Asr": j["ashar"],
            "Maghrib": j["maghrib"],
            "Isha": j["isya"],
            "Imsak": j["imsak"]
        },
        "date": {
            "gregorian": {
                "day": today.strftime("%d"),
                "month": {"en": today.strftime("%B")},
                "year": today.strftime("%Y")
            }
        }
    }

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_menu":
        await query.edit_message_text("🌙 Quyidagi islom mamlakatlaridan birini tanlang:", reply_markup=build_country_keyboard())
        return
    if query.data.startswith("prayer_"):
        try:
            index = int(query.data.split("_")[1])
            flag, country, city = ISLAMIC_COUNTRIES[index]
        except:
            await query.edit_message_text("⚠️ Xatolik.")
            return
        await query.edit_message_text("⏳ Yuklanmoqda...")
        try:
            p = get_prayer_times_new(city)
            t = p["timings"]
            g = p["date"]["gregorian"]
            msg = (
                f"📍 **{flag} {country}** ({city})\n\n"
                f"📅 **Sana:** {g['day']} {g['month']['en']} {g['year']}\n\n"
                f"🕋 **Namoz vaqtlari:**\n"
                f"🔹 **Bomdod:** {t['Fajr']} — {NAMOZ_RAKATLAR['Fajr']}\n"
                f"🔹 **Peshin:** {t['Dhuhr']} — {NAMOZ_RAKATLAR['Dhuhr']}\n"
                f"🔹 **Asr:** {t['Asr']} — {NAMOZ_RAKATLAR['Asr']}\n"
                f"🔹 **Shom:** {t['Maghrib']} — {NAMOZ_RAKATLAR['Maghrib']}\n"
                f"🔹 **Xufton:** {t['Isha']} — {NAMOZ_RAKATLAR['Isha']}\n\n"
                f"🌙 **Saharlik:** {t['Imsak']}\n"
                f"🍽️ **Iftorlik:** {t['Maghrib']}"
            )
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Yangilash", callback_data=query.data)],
                [InlineKeyboardButton("🏠 Orqaga", callback_data="back_to_menu")]
            ]))
        except Exception as e:
            logger.error(f"Xato: {e}")
            await query.edit_message_text("❌ Xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.", reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Qayta urinish", callback_data=query.data)],
                [InlineKeyboardButton("🏠 Orqaga", callback_data="back_to_menu")]
            ]))

def main():
    app = Application.builder().token(os.environ["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()

if __name__ == "__main__":
    main()
