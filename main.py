# bot.py — To'liq ishlaydigan Telegram bot: Har kuni yangi davlat

import json
import os
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# ==========================
# 1. BOT TOKEN (O'ZINGIZNI QO'YING!)
# ==========================
BOT_TOKEN = "8581071094:AAF7qK3vVOn8YUJTrlc-JEGPX3SXw5wJMoA"

# ==========================
# 2. DAVLATLAR MA'LUMOTLARI (10 ta misol — istalgancha qo'shishingiz mumkin)
# ==========================
COUNTRIES = [
    {
        "name": "O'zbekiston",
        "flag": "🇺🇿",
        "current_president": "Shavkat Mirziyoyev",
        "president_since": "2016-12-14",
        "previous_president": "Islam Karimov"
    },
    {
        "name": "Qozog'iston",
        "flag": "🇰🇿",
        "current_president": "Qosim-Jomart Toqaev",
        "president_since": "2019-03-20",
        "previous_president": "Nursulton Nazarbayev"
    },
    {
        "name": "Rossiya",
        "flag": "🇷🇺",
        "current_president": "Vladimir Putin",
        "president_since": "2012-05-07",
        "previous_president": "Dmitriy Medvedev"
    },
    {
        "name": "AQSH",
        "flag": "🇺🇸",
        "current_president": "Joe Biden",
        "president_since": "2021-01-20",
        "previous_president": "Donald Trump"
    },
    {
        "name": "Fransiya",
        "flag": "🇫🇷",
        "current_president": "Emmanuel Macron",
        "president_since": "2017-05-14",
        "previous_president": "François Hollande"
    },
    {
        "name": "Xitoy",
        "flag": "🇨🇳",
        "current_president": "Si Szinping",
        "president_since": "2013-03-15",
        "previous_president": "Xu Czinzin"
    },
    {
        "name": "Turkiya",
        "flag": "🇹🇷",
        "current_president": "Rejep Tayyip Erdo'gan",
        "president_since": "2014-08-28",
        "previous_president": "Abdullah Gul"
    },
    {
        "name": "Yaponiya",
        "flag": "🇯🇵",
        "current_president": "Fumio Kishida",
        "president_since": "2021-10-04",
        "previous_president": "Yoshihide Suga"
    },
    {
        "name": "Germaniya",
        "flag": "🇩🇪",
        "current_president": "Frank-Valter Shtaynmayer",
        "president_since": "2017-03-19",
        "previous_president": "Yoaxim Gauck"
    },
    {
        "name": "Koreya Respublikasi",
        "flag": "🇰🇷",
        "current_president": "Yun Suk Yul",
        "president_since": "2022-05-10",
        "previous_president": "Moon Jae-in"
    }
]

# ==========================
# 3. HAR KUNGI DAVLATNI BOSHQARISH
# ==========================
STATE_FILE = "daily_country.json"

def get_todays_country():
    today_str = datetime.now().strftime("%Y-%m-%d")

    # Fayl mavjud bo'lsa, o'qish
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
            if state.get("date") == today_str:
                index = state["index"]
                return COUNTRIES[index % len(COUNTRIES)]
        except (json.JSONDecodeError, KeyError):
            pass  # Agar fayl buzilgan bo'lsa, yangi yaratish

    # Yangi kun — yangi indeks (takrorlanmas ketma-ketlik)
    index = hash(today_str) % len(COUNTRIES)

    # Saqlash
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": today_str, "index": index}, f, ensure_ascii=False)

    return COUNTRIES[index]

# ==========================
# 4. TELEGRAM HANDLER
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    country = get_todays_country()
    text = (
        f"🌍 **Bugungi Davlat**: {country['flag']} {country['name']}\n\n"
        f"👤 **Hozirgi Prezident**: {country['current_president']}\n"
        f"📅 **Lavozimga kirgan**: {country['president_since']}\n"
        f"⏪ **Oldingi Prezident**: {country['previous_president']}\n\n"
        f"🤖 Har kuni 00:01 da yangi davlat tanlanadi!"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

# ==========================
# 5. BOTNI ISHGA TUSHIRISH
# ==========================
def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("✅ Bot ishga tushdi! Telegramda /start yuboring.")
    app.run_polling()

if __name__ == "__main__":
    main()
