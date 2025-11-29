import math
from datetime import datetime, date, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import pytz

# 🔑 Bot tokeningiz
BOT_TOKEN = "8581071094:AAF7qK3vVOn8YUJTrlc-JEGPX3SXw5wJMoA"

# 📅 Ramazon 2025
RAMADAN_2025 = "2025-02-28"

# 🌍 Mamlakatlar: nom, kod, bayroq, shahar, kenglik, uzunlik, vaqt zonasi
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
    {"name": "Qatar", "code": "QA", "flag": "🇶🇦", "city": "Doha", "lat": 25.2854, "lon": 51.5310, "tz": "Asia/Qatar"},
    {"name": "Kuwait", "code": "KW", "flag": "🇰🇼", "city": "Kuwait City", "lat": 29.3759, "lon": 47.9774, "tz": "Asia/Kuwait"},
    {"name": "Bangladesh", "code": "BD", "flag": "🇧🇩", "city": "Dhaka", "lat": 23.8103, "lon": 90.4125, "tz": "Asia/Dhaka"},
    {"name": "Nigeria", "code": "NG", "flag": "🇳🇬", "city": "Abuja", "lat": 9.0765, "lon": 7.3986, "tz": "Africa/Lagos"},
    {"name": "Algeria", "code": "DZ", "flag": "🇩🇿", "city": "Algiers", "lat": 36.7538, "lon": 3.0588, "tz": "Africa/Algiers"},
]

PAGE_SIZE = 5

# 📐 Astronomik yordamchi funksiyalar
def deg_to_rad(d): return d * math.pi / 180
def rad_to_deg(r): return r * 180 / math.pi

def day_of_year(d: date):
    return d.timetuple().tm_yday

def equation_of_time(day):
    M = deg_to_rad((357.5291 + 0.98560028 * day) % 360)
    C = deg_to_rad((1.9148 * math.sin(M) + 0.02 * math.sin(2*M) + 0.0003 * math.sin(3*M)) % 360)
    L = (M + C + deg_to_rad(102.9372)) % (2 * math.pi)
    return rad_to_deg(4 * (L - M)) / 60  # daqiqada

def solar_noon(day, lon):
    return 12 - equation_of_time(day) - lon / 15

def hour_angle(time, day, lat, lon, angle):
    dec = deg_to_rad(23.44 * math.sin(deg_to_rad(360/365 * (day - 81))))
    cos_h = (math.sin(deg_to_rad(angle)) - math.sin(deg_to_rad(lat)) * math.sin(dec)) / (math.cos(deg_to_rad(lat)) * math.cos(dec))
    if cos_h < -1 or cos_h > 1:
        return None
    return rad_to_deg(math.acos(cos_h)) / 15

def prayer_times(lat, lon, date_obj, tz_name):
    day = day_of_year(date_obj)
    tz = pytz.timezone(tz_name)
    today = datetime.combine(date_obj, datetime.min.time()).replace(tzinfo=tz)

    # ⏰ Quyosh tush vaqti (Peshin)
    noon = solar_noon(day, lon)
    dhuhr = today.replace(hour=int(noon), minute=int((noon % 1) * 60), second=0, microsecond=0)

    # ⏰ Bomdod (-18°) va Xufton (-18°) — Muslim World League
    fajr_h = hour_angle("fajr", day, lat, lon, -18)
    isha_h = hour_angle("isha", day, lat, lon, -18)

    if fajr_h is None or isha_h is None:
        return None

    fajr_time = noon - fajr_h
    isha_time = noon + isha_h

    # ⏰ Shom (0° — quyosh botganda)
    maghrib_h = hour_angle("maghrib", day, lat, lon, -0.833)  # -0.833 = quyosh radiusi
    if maghrib_h is None:
        return None
    maghrib_time = noon + maghrib_h

    # ⏰ Asr (Hanafi: 2x soy)
    dec = deg_to_rad(23.44 * math.sin(deg_to_rad(360/365 * (day - 81))))
    asr_angle = rad_to_deg(math.atan(2 + math.tan(deg_to_rad(lat - rad_to_deg(dec)))))
    asr_h = hour_angle("asr", day, lat, lon, -asr_angle)
    if asr_h is None:
        return None
    asr_time = noon + asr_h

    def to_time(val):
        h = int(val)
        m = int(round((val - h) * 60))
        if m >= 60:
            h += 1
            m = 0
        if h >= 24:
            h = 23
            m = 59
        return f"{h:02d}:{m:02d}"

    return {
        "Fajr": to_time(fajr_time),
        "Sunrise": to_time(noon - hour_angle("sunrise", day, lat, lon, -0.833)),
        "Dhuhr": to_time(noon),
        "Asr": to_time(asr_time),
        "Maghrib": to_time(maghrib_time),
        "Isha": to_time(isha_time),
    }

# 🔘 Tugmalar
def build_keyboard(page: int = 0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    batch = COUNTRIES[start:end]
    buttons = [[InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{c['code']}")] for c in batch]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Oldingisi", callback_data=f"page_{page-1}"))
    if end < len(COUNTRIES):
        nav.append(InlineKeyboardButton("➡️ Keyingisi", callback_data=f"page_{page+1}"))
    if nav:
        buttons.append(nav)
    return InlineKeyboardMarkup(buttons)

# 📤 /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 *Assalomu alaykum!* \n"
        "Musulmon mamlakat tanlang — Ramazon 2025 va bugungi namoz vaqtlari ko'rsatiladi.",
        parse_mode="Markdown",
        reply_markup=build_keyboard(0)
    )

# 🖱️ Tugma bosilganda
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

        tz = pytz.timezone(country["tz"])
        today = datetime.now(tz).date()
        prayers = prayer_times(country["lat"], country["lon"], today, country["tz"])

        msg = f"🌙 *{country['name']}* ({country['city']})\n"
        msg += f"📅 Ramazon 2025: *{RAMADAN_2025}*\n\n"
        msg += f"📆 Bugun: *{today.strftime('%Y-%m-%d')}*\n"

        if prayers:
            msg += "🕌 *Namoz vaqtlari (MWL usuli):*\n\n"
            msg += f"🕌 *Bomdod*: {prayers['Fajr']}\n"
            msg += f"🌅 *Quyosh*: {prayers['Sunrise']}\n"
            msg += f"🕌 *Peshin*: {prayers['Dhuhr']}\n"
            msg += f"🕌 *Asr*: {prayers['Asr']}\n"
            msg += f"🕌 *Shom*: {prayers['Maghrib']}\n"
            msg += f"🕌 *Xufton*: {prayers['Isha']}\n\n"
            msg += "✅ _Hisob Muslim World League standarti asosida amalga oshirildi._"
        else:
            msg += "\n❌ Namoz vaqtlarini hisoblashda xatolik."

        await query.edit_message_text(msg, parse_mode="Markdown")

    elif data.startswith("page_"):
        page = int(data.split("_", 1)[1])
        await query.edit_message_text("🌍 Mamlakat tanlang:", reply_markup=build_keyboard(page))

# 🚀 Asosiy
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    print("✅ Bot ishga tushdi! Start command: python app.py")
    app.run_polling()

if __name__ == "__main__":
    main()
