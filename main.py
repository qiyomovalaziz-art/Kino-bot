import math
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from astral import LocationInfo
from astral.sun import sun

# 🔑 Sizning bot tokeningiz (BU YERDA — xavfsizlik uchun Railwayda Environment Variable qilib sozlang!)
BOT_TOKEN = "8363852555:AAHb5q3veKioUh2zNMV_9EEbgvoQqOMldIg"

# 📅 Ramazon 2025 boshlanish sanasi (taxmin)
RAMADAN_2025 = "2025-02-28"

# 🌍 Musulmon mamlakatlari (10 ta asosiy)
COUNTRIES = [
    {"name": "Saudi Arabia", "code": "SA", "flag": "🇸🇦", "city": "Mecca", "lat": 21.4225, "lon": 39.8262, "tz": "Asia/Riyadh"},
    {"name": "Uzbekistan", "code": "UZ", "flag": "🇺🇿", "city": "Tashkent", "lat": 41.2995, "lon": 69.2401, "tz": "Asia/Tashkent"},
    {"name": "Indonesia", "code": "ID", "flag": "🇮🇩", "city": "Jakarta", "lat": -6.2088, "lon": 106.8456, "tz": "Asia/Jakarta"},
    {"name": "Pakistan", "code": "PK", "flag": "🇵🇰", "city": "Islamabad", "lat": 33.6844, "lon": 73.0479, "tz": "Asia/Karachi"},
    {"name": "Turkey", "code": "TR", "flag": "🇹🇷", "city": "Istanbul", "lat": 41.0082, "lon": 28.9784, "tz": "Europe/Istanbul"},
    {"name": "Egypt", "code": "EG", "flag": "🇪🇬", "city": "Cairo", "lat": 30.0444, "lon": 31.2357, "tz": "Africa/Cairo"},
    {"name": "Iran", "code": "IR", "flag": "🇮🇷", "city": "Tehran", "lat": 35.6892, "lon": 51.3890, "tz": "Asia/Tehran"},
    {"name": "Morocco", "code": "MA", "flag": "🇲🇦", "city": "Rabat", "lat": 34.0209, "lon": -6.8416, "tz": "Africa/Casablanca"},
    {"name": "Malaysia", "code": "MY", "flag": "🇲🇾", "city": "Kuala Lumpur", "lat": 3.1390, "lon": 101.6869, "tz": "Asia/Kuala_Lumpur"},
    {"name": "United Arab Emirates", "code": "AE", "flag": "🇦🇪", "city": "Dubai", "lat": 25.2048, "lon": 55.2708, "tz": "Asia/Dubai"},
]

PAGE_SIZE = 5

def build_keyboard(page: int = 0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    batch = COUNTRIES[start:end]
    buttons = [
        [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{c['code']}")]
        for c in batch
    ]
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingisi", callback_data=f"page_{page-1}"))
    if end < len(COUNTRIES):
        nav_row.append(InlineKeyboardButton("➡️ Keyingisi", callback_data=f"page_{page+1}"))
    if nav_row:
        buttons.append(nav_row)
    return InlineKeyboardMarkup(buttons)

def calculate_prayer_times(lat, lon, tz_name):
    try:
        city = LocationInfo(name="", region="", timezone=tz_name, latitude=lat, longitude=lon)
        today = datetime.today().date()
        s = sun(city.observer, date=today, tzinfo=city.timezone)

        sunrise = s['sunrise']
        sunset = s['sunset']
        noon = s['noon']

        # Namoz vaqtlari (soddalashtirilgan, lekin amaliy)
        fajr = sunrise - timedelta(minutes=90)   # Bomdod: quyoshdan 1.5 soat oldin
        dhuhr = noon                            # Peshin: tush
        asr = noon + timedelta(hours=3)         # Asr: taxminan
        maghrib = sunset                        # Shom: quyosh botganda
        isha = sunset + timedelta(minutes=90)   # Xufton: quyoshdan 1.5 soat keyin

        return {
            "Fajr": fajr.strftime("%H:%M"),
            "Sunrise": sunrise.strftime("%H:%M"),
            "Dhuhr": dhuhr.strftime("%H:%M"),
            "Asr": asr.strftime("%H:%M"),
            "Maghrib": maghrib.strftime("%H:%M"),
            "Isha": isha.strftime("%H:%M"),
        }
    except Exception as e:
        raise RuntimeError(f"Hisoblash xatolik: {str(e)}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *Assalomu alaykum!*\n\n"
        "Quyidagi musulmon mamlakatlaridan birini tanlang. "
        "Sizga **Ramazon 2025 sanasi** va **bugungi namoz vaqtlari** ko'rsatiladi.",
        parse_mode="Markdown",
        reply_markup=build_keyboard(page=0)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("country_"):
        code = data.split("_", 1)[1]
        country = next((c for c in COUNTRIES if c["code"] == code), None)
        if not country:
            await query.edit_message_text("❌ Mamlakat topilmadi.")
            return

        try:
            prayers = calculate_prayer_times(country["lat"], country["lon"], country["tz"])
            today_str = datetime.now().strftime("%Y-%m-%d")

            msg = f"🌙 *{country['name']}* ({country['city']})\n"
            msg += f"📅 *Ramazon 2025 boshlanishi*: {RAMADAN_2025}\n\n"
            msg += f"📆 *Bugungi sana*: {today_str}\n"
            msg += "🕌 *Namoz vaqtlari (taxminiy):*\n\n"
            msg += f"🕌 *Bomdod*: {prayers['Fajr']}\n"
            msg += f"🌅 *Quyosh chiqishi*: {prayers['Sunrise']}\n"
            msg += f"🕌 *Peshin*: {prayers['Dhuhr']}\n"
            msg += f"🕌 *Asr*: {prayers['Asr']}\n"
            msg += f"🕌 *Shom*: {prayers['Maghrib']}\n"
            msg += f"🕌 *Xufton*: {prayers['Isha']}\n\n"
            msg += "ℹ️ _Ma'lumotlar quyosh harakati asosida hisoblangan. Aniq vaqt uchun mahalliy masjid bilan tekshiring._"

        except Exception as e:
            msg = f"❌ Xatolik yuz berdi:\n`{str(e)}`"

        await query.edit_message_text(msg, parse_mode="Markdown")

    elif data.startswith("page_"):
        page = int(data.split("_", 1)[1])
        await query.edit_message_text(
            "🌍 Mamlakat tanlang:",
            reply_markup=build_keyboard(page=page)
        )

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("✅ Bot ishga tushdi! Railwayda ishlayapti...")
    app.run_polling()

if __name__ == "__main__":
    main()
