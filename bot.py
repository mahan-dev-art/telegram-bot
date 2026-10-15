
import os
from io import BytesIO

import requests
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_TOKEN = os.getenv("API_TOKEN")

API_URL = "https://api.majidapi.ir/instagram/download"

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN در فایل .env تنظیم نشده است")

if not API_TOKEN:
    raise ValueError("API_TOKEN در فایل .env تنظیم نشده است")

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=["start"])
def start_handler(message):
    keyboard = telebot.types.InlineKeyboardMarkup()

    keyboard.add(
        telebot.types.InlineKeyboardButton(
            "دانلودر اینستاگرام",
            callback_data="instagram_downloader"
        )
    )

    bot.send_message(
        message.chat.id,
        "سلام! 👋\n"
        "برای دانلود ویدئوی اینستاگرام، دکمه زیر را انتخاب کن.",
        reply_markup=keyboard
    )


@bot.callback_query_handler(
    func=lambda call: call.data == "instagram_downloader"
)
def callback_handler(call):
    bot.answer_callback_query(call.id)

    bot.send_message(
        call.message.chat.id,
        "🔗 لطفاً لینک پست یا ریلز اینستاگرام را ارسال کن."
    )


@bot.message_handler(
    func=lambda message: (
        bool(message.text)
        and "instagram.com/" in message.text
    )
)
def instagram_downloader(message):
    url = message.text.strip()
    chat_id = message.chat.id

    try:
        bot.send_message(
            chat_id,
            "⏳ در حال دریافت ویدئو..."
        )

        response = requests.get(
            API_URL,
            params={
                "url": url,
                "token": API_TOKEN
            },
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        videos = data.get("result", {}).get("videos", [])

        if not videos:
            bot.send_message(
                chat_id,
                "❌ ویدئویی برای این لینک پیدا نشد."
            )
            return

        video_url = videos[0].get("url")

        if not video_url:
            bot.send_message(
                chat_id,
                "❌ لینک دانلود در پاسخ API وجود ندارد."
            )
            return

        video_response = requests.get(
            video_url,
            timeout=60
        )

        video_response.raise_for_status()

        video_file = BytesIO(video_response.content)
        video_file.name = "instagram_video.mp4"

        bot.send_video(
            chat_id,
            video_file,
            timeout=120,
            supports_streaming=True
        )

    except requests.RequestException as error:
        print("Request error:", repr(error))

        bot.send_message(
            chat_id,
            "❌ در ارتباط با سرور یا دریافت ویدئو خطایی رخ داد."
        )

    except Exception as error:
        print("Unexpected error:", repr(error))

        bot.send_message(
            chat_id,
            "❌ هنگام پردازش یا ارسال ویدئو خطایی رخ داد."
        )


if __name__ == "__main__":
    # Remove webhook before starting polling.
    bot.remove_webhook()

    print("Instagram downloader bot started!")

    bot.infinity_polling(
        skip_pending=True,
        timeout=30,
        long_polling_timeout=25
    )
