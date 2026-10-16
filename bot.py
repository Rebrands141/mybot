import os
import telebot
from yt_dlp import YoutubeDL

# Token cloud website se apne aap utha lega
BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome! Mujhe kisi bhi Video/Reel ka link bhejein, main high-speed cloud se download karke dunga. Aapka data aur phone bilkul safe hai!")

@bot.message_handler(func=lambda message: True)
def download_and_send_video(message):
    url = message.text
    
    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "❌ Kripya sahi link bhejein.")
        return

    msg = bot.reply_to(message, "📥 Cloud Server video process kar raha hai... Intezar karein.")
    
    # Badi files ke liye cloud system configuration
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': 'cloud_dl_video.mp4',
        'quiet': True,
        'no_warnings': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        bot.edit_message_text("📤 Telegram par send ki ja rahi hai...", message.chat.id, msg.message_id)
        
        with open('cloud_dl_video.mp4', 'rb') as video:
            bot.send_video(
                message.chat.id, 
                video, 
                caption="✅ Downloaded successfully by Cloud Engine!",
                timeout=300, # Badi video ke liye time badhaya
                supports_streaming=True
            )
        
        os.remove('cloud_dl_video.mp4')
        bot.delete_message(message.chat.id, msg.message_id)

    except Exception as e:
        bot.edit_message_text("❌ Error: Video size bohot zyada bada hai ya platform supported nahi hai.", message.chat.id, msg.message_id)
        if os.path.exists('cloud_dl_video.mp4'):
            os.remove('cloud_dl_video.mp4')

print("Cloud Bot is running successfully...")
bot.infinity_polling()
