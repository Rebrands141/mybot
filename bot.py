import os
import io
import numpy as np
from PIL import Image, ImageEnhance, ImageOps
import telebot
from yt_dlp import YoutubeDL

BOT_TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# --- स्मार्ट फोटो एडिटिंग लॉजिक ---
def smart_auto_edit(image_bytes):
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
        
    img_np = np.array(img)
    avg_brightness = np.mean(img_np)
    
    brightness_factor = 1.05
    contrast_factor = 1.15
    saturation_factor = 1.12
    sharpness_factor = 1.30

    if avg_brightness < 80:
        brightness_factor = 1.25
        contrast_factor = 1.20
    elif avg_brightness > 180:
        brightness_factor = 0.90
        contrast_factor = 1.10
        
    img = ImageEnhance.Brightness(img).enhance(brightness_factor)
    img = ImageEnhance.Contrast(img).enhance(contrast_factor)
    img = ImageEnhance.Color(img).enhance(saturation_factor)
    img = ImageEnhance.Sharpness(img).enhance(sharpness_factor)

    r, g, b = img.split()
    r = r.point(lambda i: min(255, int(i * 1.03)))
    b = b.point(lambda i: int(i * 0.96))
    img = Image.merge('RGB', (r, g, b))

    output_buffer = io.BytesIO()
    img.save(output_buffer, format='JPEG', quality=95)
    output_buffer.seek(0)
    return output_buffer

# --- स्टार्ट और हेल्प कमांड ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "👋 Hello! Welcome to **Abhay 2-in-1 Bot**!\n\n"
        "📥 **Video Downloader:** Kisi bhi Insta/YouTube video ka link bhejein.\n"
        "📸 **AI Photo Editor:** Mujhe koi bhi photo bhejein, mai use automatic professional look me edit kar dunga!",
        parse_mode="Markdown"
    )

# --- [महत्वपूर्ण सुधार] फोटो एडिटर हैंडलर को ऊपर रखा गया है ताकि टेलीग्राम इसे पहले चेक करे ---
@bot.message_handler(content_types=['photo'])
def handle_photo_edit(message):
    msg = bot.reply_to(message, "⚡ Aapki photo ka analysis kiya ja raha hai aur professional editing jaari hai... Please wait.")
    
    try:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        edited_photo_buffer = smart_auto_edit(downloaded_file)
        
        bot.send_photo(
            message.chat.id, 
            edited_photo_buffer, 
            caption="✨ **Aapki photo professional edit ho gayi hai!**\n\n✅ Powered by Abhay AI Engine!",
            reply_to_message_id=message.message_id,
            parse_mode="Markdown"
        )
        bot.delete_message(message.chat.id, msg.message_id)
        
    except Exception as e:
        bot.edit_message_text("❌ Error: Photo edit nahi ho payi. Kripya doosri photo try karein.", message.chat.id, msg.message_id)
        print(f"Photo Edit Error: {e}")

# --- वीडियो डाउनलोडर हैंडलर (सिर्फ टेक्स्ट मैसेज के लिए काम करेगा) ---
@bot.message_handler(content_types=['text'])
def download_and_send_video(message):
    url = message.text
    
    # अगर यूजर गलती से कोई कमांड या नॉर्मल टेक्स्ट लिखे जो लिंक नहीं है
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

print("24/7 Zero-Crash 2-in-1 Bot Active...")
bot.infinity_polling()
        
