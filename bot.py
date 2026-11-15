import os
import logging
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

# Thiết lập ghi log hoạt động
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Lấy Token từ biến môi trường trên Render (an toàn, không lo lộ code)
BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")
PORT = int(os.environ.get("PORT", 10000))

# --- PHẦN 1: MỞ CỔNG PORT ĐỂ RENDER KHÔNG BÁO LỖI ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running 24/7!", 200

def run_web_server():
    app.run(host="0.0.0.0", port=PORT)

# --- PHẦN 2: XỬ LÝ TIN NHẮN TELEGRAM BOT ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Xin chào {user.first_name}!\n"
        "🤖 Bot hỗ trợ Locket Gold tự động đã sẵn sàng.\n\n"
        "Vui lòng gửi **Username** hoặc **Link tài khoản Locket** của bạn:",
        parse_mode="Markdown"
    )

async def handle_locket_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = update.message.chat_id

    processing_msg = await update.message.reply_text(
        f"⏳ Đang tiếp nhận yêu cầu cho: `{user_input}`...\nVui lòng chờ trong giây lát.",
        parse_mode="Markdown"
    )

    try:
        # --- KHU VỰC TÍCH HỢP API / CODE XỬ LÝ LOCKET ---
        # Sau này bạn sẽ gắn logic gọi API tự động tại đây
        success = True 
        
        if success:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text=f"✅ **Thành công!** Tài khoản `{user_input}` đã được xử lý.\n\n"
                     "💡 *Lưu ý:* Khởi động lại ứng dụng Locket để cập nhật.",
                parse_mode="Markdown"
            )
        else:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=processing_msg.message_id,
                text="❌ **Thất bại!** Không thể xử lý yêu cầu lúc này.",
                parse_mode="Markdown"
            )
    except Exception as e:
        logger.error(f"Lỗi: {e}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=processing_msg.message_id,
            text="⚠️ Đã có lỗi hệ thống xảy ra."
        )

def main():
    # Chạy ngầm Web Server để mở cổng Port cho Render
    web_thread = Thread(target=run_web_server)
    web_thread.daemon = True
    web_thread.start()

    # Khởi chạy Bot Telegram
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_locket_request))

    logger.info("🤖 Bot đang chạy...")
    application.run_polling()

if __name__ == '__main__':
    main()
