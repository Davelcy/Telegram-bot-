from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import json
from datetime import datetime, timedelta

# Load environment variables
import os
from dotenv import load_dotenv
load_dotenv()

# Your bot token from @BotFather
TOKEN = os.getenv("BOT_TOKEN")

# File to store chat IDs for broadcasting (owner only)
CHAT_IDS_FILE = "chat_ids.json"

# Your Telegram chat ID (owner/admin ID)
OWNER_CHAT_ID = os.getenv("OWNER_CHAT_ID")  # Replace with your Telegram chat ID

# Record the bot's start time
BOT_START_TIME = datetime.now()

# Save owner chat ID to broadcast list
def save_chat_id(chat_id):
    if str(chat_id) == OWNER_CHAT_ID:  # Only save the owner's chat ID
        try:
            with open(CHAT_IDS_FILE, 'r') as f:
                chat_ids = json.load(f)
        except FileNotFoundError:
            chat_ids = []
        if chat_id not in chat_ids:
            chat_ids.append(chat_id)
            with open(CHAT_IDS_FILE, 'w') as f:
                json.dump(chat_ids, f)

# Function to calculate and format uptime
def get_uptime():
    uptime_duration = datetime.now() - BOT_START_TIME
    days, remainder = divmod(int(uptime_duration.total_seconds()), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = []
    if days > 0:
        uptime_str.append(f"{days} day{'s' if days != 1 else ''}")
    if hours > 0:
        uptime_str.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes > 0:
        uptime_str.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds > 0 or not uptime_str:
        uptime_str.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(uptime_str)

# Handle button actions
async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = update.message.text
    uptime = get_uptime()
    
    if message_text == "Start":
        await start(update, context)
    elif message_text == "Help":
        await help_command(update, context)
    elif message_text == "Broadcast":
        await broadcast(update, context)
    elif message_text == "Message Owner":
        await message_owner(update, context)

# Define the /start command (triggered by button)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    save_chat_id(update.message.chat_id)
    keyboard = [
        ["LORD NEXUS V1 PANEL"],  # Title row
        ["Start", "Help"],        # Row 1
        ["Broadcast", "Message Owner"]  # Row 2
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)  # Persistent keyboard
    uptime = get_uptime()
    await update.message.reply_text(
        f"Welcome to LORD NEXUS V1! I am your personal assistant. Select an option from the panel below:\n"
        f"Bot Uptime: {uptime}",
        reply_markup=reply_markup
    )

# Define the /help command (triggered by button)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = get_uptime()
    await update.message.reply_text(
        f"Available commands:\n"
        f"Start - Welcome the user\n"
        f"Help - Get this help message\n"
        f"Broadcast - Send a message to all subscribers (owner only)\n"
        f"Message Owner - Send a message to the bot owner\n"
        f"Bot Uptime: {uptime}"
    )

# Define the /broadcast command (owner only, triggered by button)
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.chat_id) != OWNER_CHAT_ID:
        await update.message.reply_text("Only the bot owner can send broadcast messages!")
        return
    if not context.args:
        await update.message.reply_text("Please provide a message to broadcast, e.g., Broadcast Hello everyone!")
        return
    message = " ".join(context.args)
    try:
        with open(CHAT_IDS_FILE, 'r') as f:
            chat_ids = json.load(f)
    except FileNotFoundError:
        await update.message.reply_text("No subscribers found.")
        return
    for chat_id in chat_ids:
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            print(f"Failed to send to {chat_id}: {e}")
    uptime = get_uptime()
    await update.message.reply_text(f"Broadcast sent successfully!\nBot Uptime: {uptime}")

# Define the /messageowner command (triggered by button)
async def message_owner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Please provide a message, e.g., Message Owner Hello, I need help!")
        return
    message = " ".join(context.args)
    try:
        await context.bot.send_message(chat_id=OWNER_CHAT_ID, text=f"New message from {update.message.from_user.username}: {message}")
        uptime = get_uptime()
        await update.message.reply_text(f"Your message has been sent to the owner!\nBot Uptime: {uptime}")
    except Exception as e:
        await update.message.reply_text("Failed to send message. Please try again later.")

# Main function to start the bot
async def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("messageowner", message_owner))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button))

    await app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())