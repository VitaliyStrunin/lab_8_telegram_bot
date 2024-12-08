import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
import os

TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
USER_MAIL = os.environ.get('USER_MAIL_LAB_8')
USER_PASSWORD = os.environ.get('USER_PASSWORD_LAB_8')

def validate_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Приветствую! Напишите e-mail, на который нужно отправить сообщение!")
    return 0

async def receive_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text
    if validate_email(email):
        context.user_data['email'] = email
        await update.message.reply_text("e-mail принят, введите сообщение")
        return 1
    else:
        await update.message.reply_text("e-mail некорректный, повторите ввод")
        return 0

async def receive_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    recipient_email = context.user_data.get('email')

    smtp_server = "smtp.yandex.ru"
    smtp_port = 587
    sender_email = USER_MAIL
    sender_password = USER_PASSWORD

    try:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = "Сообщение от бота (лабораторка 8)"
        msg.attach(MIMEText(message_text, 'plain'))
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        await update.message.reply_text("Сообщение успешно отправлено на указанный email!")
    except Exception as e:
        await update.message.reply_text(f"Не удалось отправить сообщение. Ошибка: {str(e)}")

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Операция отменена.")
    return ConversationHandler.END


# Основная функция
def main():
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            0: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_email)],
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(handler)
    application.run_polling()


if __name__ == "__main__":
    main()
