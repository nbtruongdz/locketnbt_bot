import os
import logging
from datetime import datetime
from threading import Thread
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token chính xác của bạn từ BotFather
BOT_TOKEN = "9090276660:AAGtSJbUiFKjjCUyvdfwlCDbse6A7Yq0nek"
PORT = int(os.environ.get("PORT", 10000))

# Khởi tạo Web Server Flask để mở cổng duy trì 24/7 trên Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

def run_web_server():
    app.run(host="0.0.0.0", port=PORT)

# Khởi tạo Telegram Bot với telebot
bot = telebot.TeleBot(BOT_TOKEN)

# Hàm hỗ trợ lưu thông tin khách hàng vào file clients.txt
def save_client_to_file(user_input, user_info):
    filename = "clients.txt"
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    user_id = user_info.id
    username = f"@{user_info.username}" if user_info.username else "Không có username"
    full_name = f"{user_info.first_name or ''} {user_info.last_name or ''}".strip()
    
    log_line = f"[{time_now}] ID: {user_id} | Tên: {full_name} | Username: {username} | Nội dung gửi: {user_input}\n"
    
    try:
        with open(filename, "a", encoding="utf-8") as f:
            f.write(log_line)
        logger.info(f"Đã lưu thông tin khách: {user_input}")
    except Exception as e:
        logger.error(f"Lỗi ghi file: {e}")

# Lệnh /start: Chào mừng khách hàng kèm ảnh giới thiệu
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_photo_url = "https://i.imgur.com/4AiX2q6.png" 
    
    caption_text = (
        "Xin chào! 🤖 Chào mừng bạn đến với hệ thống hỗ trợ **Locket Gold** tự động.\n\n"
        "✨ Nâng cấp tài khoản mượt mà, nhanh chóng, uy tín.\n"
        "👇 Vui lòng gửi **Username** hoặc **Link tài khoản Locket** của bạn để bắt đầu:"
    )
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📌 Hướng dẫn sử dụng", url="https://t.me/"))

    try:
        bot.send_photo(
            chat_id=message.chat.id,
            photo=welcome_photo_url,
            caption=caption_text,
            parse_mode="Markdown",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Lỗi gửi ảnh /start: {e}")
        bot.send_message(message.chat.id, caption_text, parse_mode="Markdown")

# Xử lý khi khách hàng gửi Username hoặc Link Locket
@bot.message_handler(func=lambda message: True)
def handle_locket_request(message):
    user_input = message.text.strip()
    
    # 1. Lưu lại thông tin khách hàng vào file clients.txt
    save_client_to_file(user_input, message.from_user)
    
    # 2. Gửi tin nhắn đang chờ xử lý (dùng send_message thay vì reply_to để tránh lỗi mất message gốc)
    msg = bot.send_message(
        message.chat.id, 
        f"⏳ Đang tiếp nhận yêu cầu nâng cấp Locket Gold cho tài khoản: `{user_input}`...\nVui lòng chờ trong giây lát.", 
        parse_mode="Markdown"
    )
    
    try:
        # --- KHU VỰC XỬ LÝ LOGIC NÂNG CẤP LOCKET GOLD ---
        success = True # Giả lập xử lý thành công
        
        result_photo_url = "https://i.imgur.com/4AiX2q6.png" 
        success_caption = (
            f"✅ **Thành công!** Tài khoản `{user_input}` đã được kích hoạt **Locket Gold**.\n\n"
            "💡 *Lưu ý:* Vui lòng khởi động lại (đóng hoàn toàn) ứng dụng Locket trên điện thoại để cập nhật tính năng mới."
        )
        
        if success:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg.message_id)
            except Exception:
                pass
            bot.send_photo(
                chat_id=message.chat.id,
                photo=result_photo_url,
                caption=success_caption,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                "❌ **Thất bại!** Không thể xử lý yêu cầu lúc này, vui lòng thử lại sau.",
                chat_id=message.chat.id,
                message_id=msg.message_id,
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Lỗi xử lý: {e}")
        bot.send_message(message.chat.id, "⚠️ Đã có lỗi hệ thống xảy ra.")

def main():
    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    logger.info(f"🌐 Flask Web Server đã mở tại cổng: {PORT}")

    logger.info("🤖 Bot đang chạy polling...")
    bot.infinity_polling()

if __name__ == '__main__':
    main()
