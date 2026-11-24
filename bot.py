
import os
import secrets
import string
import logging

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
PTC_URL = "https://club.pokemon.com/"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def generate_username():
    return "Trainer" + "".join(
        secrets.choice(string.digits) for _ in range(8)
    )

def generate_password():
    chars = string.ascii_letters + string.digits + "!@#$%"
    return "".join(secrets.choice(chars) for _ in range(16))


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
            "🌐 Open PTC Website",
            url=PTC_URL
        )]
    ]

    await query.message.reply_text(
        "🎮 REGISTRATION STARTED\n\n"
        f"Suggested Username: `{username}`\n"
        f"Suggested Password: `{password}`\n\n"
        "Complete the official registration yourself.\n"
        "CAPTCHA and email verification must be completed "
        "on the official website.\n\n"
        "⚠️ Keep your credentials private.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 MINATO PTC BOT HELP\n\n"
        "/start - Start bot\n"
        "/create - Registration assistant\n"
        "/help - Help menu"
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


def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN missing in environment!")

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(buttons))

    print("MINATO PTC BOT IS RUNNING!")

    app.run_polling()


if __name__ == "__main__":
    main()
