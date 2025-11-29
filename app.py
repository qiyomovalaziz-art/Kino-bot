import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = ("8363852555:AAHb5q3veKioUh2zNMV_9EEbgvoQqOMldIg")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN muhit o'zgaruvchisi sozlanmagan!")

# 📅 2025-yil uchun Ramazon boshlanish sanasi (astronomik taxmin — 28-fevral ko'pincha ishonchli)
# Barcha mamlakatlar uchun bir xil sana qo'llaniladi (haqiqatda 1 kun farq qilishi mumkin)
RAMADAN_2025 = "2025-02-28"

# 🌍 OIC (Islom Hamkorligi Tashkiloti) a'zolaridan 49 ta mamlakat
# Manba: https://www.oic-oci.org/member-states/
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

# Sahifadagi mamlakat soni
PAGE_SIZE = 5

def build_keyboard(page: int = 0):
    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    batch = MUSLIM_COUNTRIES[start:end]

    # Bayroq + nom tugmalari
    buttons = [
        [InlineKeyboardButton(f"{c['flag']} {c['name']}", callback_data=f"country_{c['code']}")]
        for c in batch
    ]

    # Navigatsiya tugmalari (pastda)
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Oldingisi", callback_data=f"page_{page-1}"))
    if end < len(MUSLIM_COUNTRIES):
        nav_row.append(InlineKeyboardButton("➡️ Keyingisi", callback_data=f"page_{page+1}"))
    
    if nav_row:
        buttons.append(nav_row)

    return InlineKeyboardMarkup(buttons)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi musulmon mamlakatlaridan birini tanlang, "
        "2025-yilda Ramazon oyi qachon boshlanishini bilib oling:",
        reply_markup=build_keyboard(page=0)
    )

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("country_"):
        code = data.split("_", 1)[1]
        country = next((c for c in MUSLIM_COUNTRIES if c["code"] == code), None)
        if country:
            msg = (
                f"🌙 *{country['name']}* davlati uchun Ramazon 2025:\n"
                f"📅 Boshlanish sanasi: *{RAMADAN_2025}*\n\n"
                "⚠️ Eslatma: Haqiqiy sana hilol kuzatish natijasiga qarab 1 kun oldin yoki keyin bo'lishi mumkin."
            )
            await query.edit_message_text(msg, parse_mode="Markdown")
        else:
            await query.edit_message_text("❌ Mamlakat topilmadi.")

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
    print("✅ Bot ishga tushdi! Railwayda ishlayapti.")
    app.run_polling()

if __name__ == "__main__":
    main()
