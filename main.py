import os
import requests
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Tokenni to'g'ridan-to'g'ri kiritdingiz — .env kerak emas
BOT_TOKEN = "8363852555:AAHb5q3veKioUh2zNMV_9EEbgvoQqOMldIg"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN sozlanmagan!")

# 📍 Har bir mamlakat uchun namoz vaqtlari uchun asosiy shahar
# Aladhan API mamlakat kodini emas, shahar + mamlakat nomini talab qiladi
COUNTRY_CITIES = {
    "SA": ("Mecca", "Saudi Arabia"),
    "UZ": ("Tashkent", "Uzbekistan"),
    "ID": ("Jakarta", "Indonesia"),
    "PK": ("Islamabad", "Pakistan"),
    "TR": ("Istanbul", "Turkey"),
    "EG": ("Cairo", "Egypt"),
    "IR": ("Tehran", "Iran"),
    "MA": ("Rabat", "Morocco"),
    "MY": ("Kuala Lumpur", "Malaysia"),
    "AE": ("Dubai", "United Arab Emirates"),
    "QA": ("Doha", "Qatar"),
    "KW": ("Kuwait City", "Kuwait"),
    "OM": ("Muscat", "Oman"),
    "BH": ("Manama", "Bahrain"),
    "BD": ("Dhaka", "Bangladesh"),
    "NG": ("Abuja", "Nigeria"),
    "DZ": ("Algiers", "Algeria"),
    "SD": ("Khartoum", "Sudan"),
    "IQ": ("Baghdad", "Iraq"),
    "AF": ("Kabul", "Afghanistan"),
    "YE": ("Sana'a", "Yemen"),
    "SY": ("Damascus", "Syria"),
    "JO": ("Amman", "Jordan"),
    "LB": ("Beirut", "Lebanon"),
    "PS": ("Ramallah", "Palestine"),
    "TN": ("Tunis", "Tunisia"),
    "LY": ("Tripoli", "Libya"),
    "SN": ("Dakar", "Senegal"),
    "ML": ("Bamako", "Mali"),
    "NE": ("Niamey", "Niger"),
    "TD": ("N'Djamena", "Chad"),
    "SO": ("Mogadishu", "Somalia"),
    "DJ": ("Djibouti", "Djibouti"),
    "KM": ("Moroni", "Comoros"),
    "MR": ("Nouakchott", "Mauritania"),
    "BN": ("Bandar Seri Begawan", "Brunei"),
    "MV": ("Malé", "Maldives"),
    "GN": ("Conakry", "Guinea"),
    "SL": ("Freetown", "Sierra Leone"),
    "GM": ("Banjul", "Gambia"),
    "GW": ("Bissau", "Guinea-Bissau"),
    "BF": ("Ouagadougou", "Burkina Faso"),
    "BJ": ("Porto-Novo", "Benin"),
    "TG": ("Lomé", "Togo"),
    "GA": ("Libreville", "Gabon"),
    "CM": ("Yaoundé", "Cameroon"),
    "CF": ("Bangui", "Central African Republic"),
    "MZ": ("Maputo", "Mozambique"),
    "UG": ("Kampala", "Uganda"),
}

RAMADAN_2025 = "2025-02-28"

MUSLIM_COUNTRIES = [
    {"name": "Saudi Arabia", "code": "SA", "flag": "🇸🇦"},
    {"name": "Uzbekistan", "code": "UZ", "flag": "🇺🇿"},
    {"name": "Indonesia", "code": "ID", "flag": "🇮🇩"},
    {"name": "Pakistan", "code": "PK", "flag": "🇵🇰"},
    {"name": "Turkey", "code": "TR", "flag": "🇹🇷"},
    {"name": "Egypt", "code": "EG", "flag": "🇪🇬"},
    {"name": "Iran", "code": "IR", "flag": "🇮🇷"},
    {"name": "Morocco", "code": "MA", "flag": "🇲🇦"},
    {"name": "Malaysia", "code": "MY", "flag": "🇲🇾"},
    {"name": "United Arab Emirates", "code": "AE", "flag": "🇦🇪"},
    {"name": "Qatar", "code": "QA", "flag": "🇶🇦"},
    {"name": "Kuwait", "code": "KW", "flag": "🇰🇼"},
    {"name": "Oman", "code": "OM", "flag": "🇴🇲"},
    {"name": "Bahrain", "code": "BH", "flag": "🇧🇭"},
    {"name": "Bangladesh", "code": "BD", "flag": "🇧🇩"},
    {"name": "Nigeria", "code": "NG", "flag": "🇳🇬"},
    {"name": "Algeria", "code": "DZ", "flag": "🇩🇿"},
    {"name": "Sudan", "code": "SD", "flag": "🇸🇩"},
    {"name": "Iraq", "code": "IQ", "flag": "🇮🇶"},
    {"name": "Afghanistan", "code": "AF", "flag": "🇦🇫"},
    {"name": "Yemen", "code": "YE", "flag": "🇾🇪"},
    {"name": "Syria", "code": "SY", "flag": "🇸🇾"},
    {"name": "Jordan", "code": "JO", "flag": "🇯🇴"},
    {"name": "Lebanon", "code": "LB", "flag": "🇱🇧"},
    {"name": "Palestine", "code": "PS", "flag": "🇵🇸"},
    {"name": "Tunisia", "code": "TN", "flag": "🇹🇳"},
    {"name": "Libya", "code": "LY", "flag": "🇱🇾"},
    {"name": "Senegal", "code": "SN", "flag": "🇸🇳"},
    {"name": "Mali", "code": "ML", "flag": "🇲🇱"},
    {"name": "Niger", "code": "NE", "flag": "🇳🇪"},
    {"name": "Chad", "code": "TD", "flag": "🇹🇩"},
    {"name": "Somalia", "code": "SO", "flag": "🇸🇴"},
    {"name": "Djibouti", "code": "DJ", "flag": "🇩🇯"},
    {"name": "Comoros", "code": "KM", "flag": "🇰🇲"},
    {"name": "Mauritania", "code": "MR", "flag": "🇲🇷"},
    {"name": "Brunei", "code": "BN", "flag": "🇧🇳"},
    {"name": "Maldives", "code": "MV", "flag": "🇲🇻"},
    {"name": "Guinea", "code": "GN", "flag": "🇬🇳"},
    {"name": "Sierra Leone", "code": "SL", "flag": "🇸🇱"},
    {"name": "Gambia", "code": "GM", "flag": "🇬🇲"},
    {"name": "Guinea-Bissau", "code": "GW", "flag": "🇬🇼"},
    {"name": "Burkina Faso", "code": "BF", "flag": "🇧🇫"},
    {"name": "Benin", "code": "BJ", "flag": "🇧🇯"},
    {"name": "Togo", "code": "TG", "flag": "🇹🇬"},
    {"name": "Gabon", "code": "GA", "flag": "🇬🇦"},
    {"name": "Cameroon", "code": "CM", "flag": "🇨🇲"},
    {"name": "Central African Republic", "code": "CF", "flag": "🇨🇫"},
    {"name": "Mozambique", "code": "MZ", "flag": "🇲🇿"},
    {"name": "Uganda", "code": "UG", "flag": "🇺🇬"},
]

PAGE_SIZE = 5

def build_keyboard(page: int = 0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    batch = MUSLIM_COUNTRIES[start:end]
    buttons = [
        [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{c['code']}")]
        for c in batch
    ]
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingisi", callback_data=f"page_{page-1}"))
    if end < len(MUSLIM_COUNTRIES):
        nav_row.append(InlineKeyboardButton("➡️ Keyingisi", callback_data=f"page_{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    return InlineKeyboardMarkup(buttons)

def get_prayer_times(country_code):
    if country_code not in COUNTRY_CITIES:
        return None
    city, country = COUNTRY_CITIES[country_code]
    try:
        url = f"http://api.aladhan.com/v1/timingsByCity?city={city}&country={country}&method=2"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200:
                return data["data"]["timings"]
    except Exception:
        pass
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi musulmon mamlakatlaridan birini tanlang, "
        "Ramazon sanasini va bugungi namoz vaqtlarini bilib oling:",
        reply_markup=build_keyboard(page=0)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("country_"):
        code = data.split("_", 1)[1]
        country = next((c for c in MUSLIM_COUNTRIES if c["code"] == code), None)
        if not country:
            await query.edit_message_text("❌ Mamlakat topilmadi.")
            return

        # Namoz vaqtlarini olish
        prayers = get_prayer_times(code)
        today = datetime.now().strftime("%Y-%m-%d")

        msg = f"🌙 *{country['name']}* uchun ma'lumotlar:\n"
        msg += f"📅 Ramazon 2025 boshlanishi: *{RAMADAN_2025}*\n\n"

        if prayers:
            # Namoz nomlari o'zbek tilida
            prayer_names = {
                "Fajr": "🕌 Bomdod",
                "Sunrise": "🌅 Quyosh chiqishi",
                "Dhuhr": "🕌 Peshin",
                "Asr": "🕌 Asr",
                "Maghrib": "🕌 Shom",
                "Isha": "🕌 Xufton"
            }
            msg += f"📆 *Bugun: {today}*\n"
            msg += "⏱️ *Namoz vaqtlari:*\n\n"
            for key in ["Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                if key in prayers:
                    time = prayers[key]
                    name = prayer_names.get(key, key)
                    msg += f"{name}: *{time}*\n"
        else:
            msg += "⚠️ Namoz vaqtlari hozircha mavjud emas."

        msg += "\n\nℹ️ Ma'lumotlar: Aladhan API orqali olingan."

        await query.edit_message_text(msg, parse_mode="Markdown")

    elif data.startswith("page_"):
        page = int(data.split("_", 1)[1])
        await query.edit_message_text(
            "🌙 Musulmon mamlakatni tanlang:",
            reply_markup=build_keyboard(page=page)
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
