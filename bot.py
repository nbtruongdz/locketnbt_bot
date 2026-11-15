import os
import logging
from threading import Thread
from flask import Flask
import telebot

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token chính xác lấy từ ảnh BotFather của bạn
BOT_TOKEN = "9090276660:AAGtSJbUiFKjjCUyvdfwlCDbse6A7Yq0nek"
PORT = int(os.environ.get("PORT", 10000))

# Khởi tạo Web Server Flask để mở cổng trên Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

def run_web_server():
    app.run(host="0.0.0.0", port=PORT)

# Khởi tạo Telegram Bot với biến BOT_TOKEN
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Xin chào! 🤖 Bot hỗ trợ Locket Gold tự động đã sẵn sàng.\n\nVui lòng gửi Username hoặc Link tài khoản Locket của bạn:"
    )

@bot.message_handler(func=lambda message: True)
def handle_locket_request(message):
    user_input = message.text.strip()
    msg = bot.reply_to(message, f"⏳ Đang tiếp nhận yêu cầu cho: `{user_input}`...\nVui lòng chờ trong giây lát.", parse_mode="Markdown")
    
    try:
        # --- KHU VỰC XỬ LÝ LOGIC LOCKET ---
        success = True # Giả lập xử lý thành công
        
        if success:
            bot.edit_message_text(
                f"✅ **Thành công!** Tài khoản `{user_input}` đã được xử lý.\n\n💡 *Lưu ý:* Khởi động lại ứng dụng Locket để cập nhật.",
                chat_id=message.chat.id,
                message_id=msg.message_id,
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text(
                "❌ **Thất bại!** Không thể xử lý yêu cầu lúc này.",
                chat_id=message.chat.id,
                message_id=msg.message_id,
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        bot.reply_to(message, "⚠️ Đã có lỗi hệ thống xảy ra.")

def main():
    # Chạy Flask ở luồng phụ
    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()
    logger.info(f"🌐 Flask Web Server đã mở tại cổng: {PORT}")

    # Chạy Bot Telegram ở luồng chính
    logger.info("🤖 Bot đang chạy polling...")
    bot.infinity_polling()

if __name__ == '__main__':
    main()
