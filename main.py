import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)

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
    await update.message.reply_text(
        "🌙 Assalomu alaykum! Quyidagi islom mamlakatlaridan birini tanlang:",
        reply_markup=build_country_keyboard()
    )

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
        except:
            await query.edit_message_text("⚠️ Xatolik yuz berdi.")
            return

        # ⚠️ VAQTINCHALIK NAMUNA MA'LUMOT (API ishlamaguncha)
        msg = (
            f"📍 **{flag} {country}** ({city})\n\n"
            f"📅 **Sana:** 30 November 2025\n\n"
            f"🕋 **Namoz vaqtlari:**\n"
            f"🔹 **Bomdod (Fajr):** 05:30 — {NAMOZ_RAKATLAR['Fajr']}\n"
            f"🔹 **Peshin (Dhuhr):** 12:45 — {NAMOZ_RAKATLAR['Dhuhr']}\n"
            f"🔹 **Asr:** 15:20 — {NAMOZ_RAKATLAR['Asr']}\n"
            f"🔹 **Shom (Maghrib):** 17:50 — {NAMOZ_RAKATLAR['Maghrib']}\n"
            f"🔹 **Xufton (Isha):** 19:10 — {NAMOZ_RAKATLAR['Isha']}\n\n"
            f"🌙 **Saharlik (Imsak):** 05:15\n"
            f"🍽️ **Iftorlik:** 17:50"
        )

        refresh = InlineKeyboardButton("🔄 Yangilash", callback_data=query.data)
        back = InlineKeyboardButton("⬅️ Orqaga", callback_data="back_to_menu")
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([[refresh, back]]))

def main():
    app = Application.builder().token(os.environ["TOKEN"]).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.run_polling()

if __name__ == "__main__":
    main()
