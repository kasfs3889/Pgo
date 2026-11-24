
import os
import time
import logging
import threading
import secrets
import string

from flask import Flask, jsonify
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
PORT = int(os.getenv("PORT", 10000))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

app = Flask(__name__)

bot_status = {
    "running": False,
    "last_error": None
}


# Flask health server

@app.route("/")
def home():
    return jsonify({
        "name": "MINATO PTC BOT",
        "status": "online"
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "telegram_bot": bot_status["running"]
    })


# Generators

def generate_username():
    return "Trainer" + "".join(
        secrets.choice(string.digits) for _ in range(8)
    )


def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(
        secrets.choice(chars) for _ in range(16)
    )


# Telegram commands

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton(
            "🆕 Create PTC Account",
            callback_data="create"
        )],
        [InlineKeyboardButton(
            "❓ Help",
            callback_data="help"
        )]
    ]

    await update.message.reply_text(
        "⚡ Welcome to MINATO PTC BOT!\n\n"
        "Pokémon Trainer Club Registration Assistant.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    username = generate_username()
    password = generate_password()

    keyboard = [
        [InlineKeyboardButton(
            "🌐 Open Official PTC Website",
            url="https://club.pokemon.com/"
        )]
    ]

    await query.message.reply_text(
        "🎮 REGISTRATION STARTED\n\n"
        f"Suggested Username: `{username}`\n\n"
        f"Suggested Password: `{password}`\n\n"
        "Complete registration on the official website.\n"
        "CAPTCHA and email verification must be completed "
        "by you.\n\n"
        "Keep your password private.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Start bot\n"
        "/create - Start registration\n"
        "/help - Help"
    )


async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    if query.data == "create":
        await create(update, context)

    elif query.data == "help":
        await query.answer()
        await query.message.reply_text(
            "Use /create to start registration."
        )


# Telegram bot runner

def telegram_runner():
    while True:
        try:
            bot_status["running"] = True
            bot_status["last_error"] = None

            telegram_app = (
                Application.builder()
                .token(BOT_TOKEN)
                .build()
            )

            telegram_app.add_handler(
                CommandHandler("start", start)
            )

            telegram_app.add_handler(
                CommandHandler("help", help_command)
            )

            telegram_app.add_handler(
                CallbackQueryHandler(buttons)
            )

            logging.info("Telegram bot starting...")

            telegram_app.run_polling(
                drop_pending_updates=False
            )

            logging.warning("Bot polling stopped.")

        except Exception as error:
            bot_status["last_error"] = str(error)
            logging.exception("Telegram bot crashed!")

        finally:
            bot_status["running"] = False

        logging.info("Restarting bot in 10 seconds...")
        time.sleep(10)


# Main

def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN is missing!")

    bot_thread = threading.Thread(
        target=telegram_runner,
        daemon=True
    )

    bot_thread.start()

    logging.info("Starting Flask server...")

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":
    main()
