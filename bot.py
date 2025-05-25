from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import os 
TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

#  Helper: Reset user state


def reset_user_state(user_data):
    for key in ["expecting_question", "expecting_feedback", "expecting_contact"]:
        user_data[key] = False

#  Inline Keyboard


def get_inline_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❓ Ask a Question", callback_data="ask_question")],
        [InlineKeyboardButton("📝 Send Feedback", callback_data="send_feedback")],
        [InlineKeyboardButton("☎️ Contact Amir", callback_data="contact_amir")],
        [InlineKeyboardButton("📶 Join Channel", url="https://t.me/+dbm2e44puwcyZjBk")]
    ])

# === /start Command ===


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Minimal Reply Keyboard (just one menu button)
    reply_markup = ReplyKeyboardMarkup(
        [[KeyboardButton("📋 Menu")]],
        resize_keyboard=True
    )

    await update.message.reply_text(
        "👋 Welcome to CHMS Comparative Sector Bot!\nChoose an option below:",
        reply_markup=get_inline_menu()
    )

    await update.message.reply_text(
        "📍 You can also tap the '📋 Menu' button below anytime.",
        reply_markup=reply_markup
    )

# Handle Inline Button Clicks


async def inline_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_data = context.user_data
    user = query.from_user

    await query.answer()
    reset_user_state(user_data)

    if query.data == "ask_question":
        user_data["expecting_question"] = True
        await query.message.reply_text("📝 Please type your question below:")

    elif query.data == "send_feedback":
        user_data["expecting_feedback"] = True
        await query.message.reply_text("📢 Please type your feedback below:")

    elif query.data == "contact_amir":
        user_data["expecting_contact"] = True
        await query.message.reply_text("✉️ Contact Amir at @AbuMahir11\nOr type your message for Amir:")

# Handle User Messages


async def input_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    user_data = context.user_data
    user = update.message.from_user

    # If user pressed "📋 Menu" reply button
    if user_input == "📋 Menu":
        await update.message.reply_text(
            "📋 Choose an option from the menu:",
            reply_markup=get_inline_menu()
        )
        return

    # Handle question
    if user_data.get("expecting_question"):
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"❓ *New Question*\nFrom: {user.full_name} (@{user.username})\n\n{user_input}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Your question has been sent. Shukran!")
        reset_user_state(user_data)
        await update.message.reply_text("What would you like to do next?", reply_markup=get_inline_menu())
        return

    # Handle feedback
    if user_data.get("expecting_feedback"):
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"💬 *New Feedback*\nFrom: {user.full_name} (@{user.username})\n\n{user_input}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Shukran for your feedback!")
        reset_user_state(user_data)
        await update.message.reply_text("What would you like to do next?", reply_markup=get_inline_menu())
        return

    # Handle message to Amir
    if user_data.get("expecting_contact"):
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"📨 *Message for Amir*\nFrom: {user.full_name} (@{user.username})\n\n{user_input}",
            parse_mode="Markdown"
        )
        await update.message.reply_text("✅ Your message has been sent to Amir.")
        reset_user_state(user_data)
        await update.message.reply_text("What would you like to do next?", reply_markup=get_inline_menu())
        return

    # Fallback for unrecognized input
    await update.message.reply_text("❗ I didn't understand that. Use the 📋 Menu button.")

#  Run Bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(inline_menu_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, input_handle))

print("🤖 Bot is running...")
app.run_polling()
