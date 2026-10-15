import telebot
import requests


bot = telebot.TeleBot("8989728786:AAF1q1UIxRohhggAajo9TerlEU1Z5h4jaxA")

API_URL = "https://api.majidapi.ir/instagram/download"


@bot.message_handler(commands=["start"])
def start_handler(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            "دانلودر اینستاگرام",
            callback_data="/instagram-downloader"
        )
    )

    bot.send_message(
        message.chat.id,
        "سلام! من یک ربات تلگرام هستم. لطفاً دستور مورد نظر خود را انتخاب کنید.",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "/instagram-downloader":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "لطفاً لینک پست یا ریلز اینستاگرام را ارسال کنید."
        )



@bot.message_handler(func=lambda message: message.text and "instagram.com/" in message.text)
def instagram_downloader(message):
    url = message.text.strip()

    try:
        bot.send_message(message.chat.id, "⏳ در حال دریافت ویدئو...")

        response = requests.get(
            API_URL,
            params={
                "url": url,
                "token": "ugcnzj3ahbbx9kg:Vzog7ojvKLZwFuKVwi92"
            },
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        videos = data.get("result", {}).get("videos", [])

        if not videos:
            bot.send_message(
                message.chat.id,
                "❌ ویدئویی برای این لینک پیدا نشد."
            )
            return

        video_url = videos[0].get("url")

        if not video_url:
            bot.send_message(
                message.chat.id,
                "❌ لینک دانلود در پاسخ API وجود ندارد."
            )
            return

        video_response = requests.get(video_url, timeout=60)
        video_response.raise_for_status()

        from io import BytesIO

        video_file = BytesIO(video_response.content)
        video_file.name = "instagram_video.mp4"

        bot.send_video(
            message.chat.id,
            video_file,
            timeout=120,
            supports_streaming=True
        )

    
    except requests.RequestException as error:
        print("Request error:", repr(error))

        if getattr(error, "response", None) is not None:
            print("HTTP Status:", error.response.status_code)
            print("Response:", error.response.text[:1000])

        bot.send_message(
            message.chat.id,
            f"❌ خطا در دریافت ویدئو:\n{str(error)[:500]}"
        )


    except Exception as error:
        print("Error:", error)
        bot.send_message(
            message.chat.id,
            "❌ هنگام ارسال ویدئو خطایی رخ داد."
        )


bot.remove_webhook()
bot.infinity_polling(skip_pending=True)