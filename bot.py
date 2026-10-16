import os
import telebot
from yt_dlp import YoutubeDL

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# Yahan aapka bataya hua naya welcome message add kar diya hai
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "hello welcome abhay downloader bot")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "❌ Sahi link bhejein.")
        return

    msg = bot.reply_to(message, "⚡ Badi video hai, Direct Cloud Stream Active ho raha hai... Chat me hi video milegi.")
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            video_url = info.get('url', None)
            video_title = info.get('title', 'Video')
            
        if video_url:
            bot.edit_message_text("📤 Video mil gayi hai, Telegram Server par transfer ho rahi hai...", message.chat.id, msg.message_id)
            
            bot.send_video(
                message.chat.id, 
                video_url, 
                caption=f"🎥 **Title:** {video_title}\n\n✅ Powered by Abhay Engine!",
                supports_streaming=True,
                timeout=600
            )
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            raise Exception

    except Exception as e:
        if 'video_url' in locals() and video_url:
            bot.edit_message_text(
                f"🎬 **Title:** {video_title}\n\n"
                f"⚠️ Video size bohot bada hai, Telegram direct file block kar raha hai. Niche click karke 1-click me direct save karein:\n\n"
                f"📥 [⚡ Direct Download Link]({video_url})",
                message.chat.id, 
                msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text("❌ Error: Video load nahi ho payi. Link private ho sakta hai.", message.chat.id, msg.message_id)

print("24/7 Zero-Crash Bot Active...")
bot.infinity_polling()
