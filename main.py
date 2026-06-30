import os
import re
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable (Railway)
BOT_TOKEN = os.environ.get("BOT_TOKEN") or os.environ.get("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not set!")

# User sessions to track analysis mode
user_sessions = {}

# ============ HELPER FUNCTIONS ============

def count_words(text: str) -> dict:
    """Count words, characters, sentences, paragraphs, and reading time."""
    # Word count
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    
    # Character count
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    
    # Sentence count (split by ., !, ?)
    sentences = re.split(r"[.!?]+", text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Paragraph count (split by newlines)
    paragraphs = [p for p in text.split("\n") if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Reading time (average 200 words per minute)
    reading_time_min = word_count / 200 if word_count > 0 else 0
    reading_time_sec = reading_time_min * 60
    
    # Speaking time (average 150 words per minute)
    speaking_time_min = word_count / 150 if word_count > 0 else 0
    
    # Longest word
    longest_word = max(words, key=len) if words else "None"
    
    # Average word length
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "reading_time_min": round(reading_time_min, 1),
        "reading_time_sec": round(reading_time_sec, 0),
        "speaking_time_min": round(speaking_time_min, 1),
        "longest_word": longest_word,
        "avg_word_length": round(avg_word_length, 1),
    }

def format_stats(stats: dict) -> str:
    """Format statistics into a readable message."""
    return f"""
📊 **Text Statistics**

📝 **Words:** `{stats['word_count']}`
✏️ **Characters (with spaces):** `{stats['char_count']}`
📏 **Characters (no spaces):** `{stats['char_count_no_spaces']}`
📄 **Sentences:** `{stats['sentence_count']}`
📑 **Paragraphs:** `{stats['paragraph_count']}`

⏱️ **Reading Time:** `{stats['reading_time_min']} min` ({stats['reading_time_sec']} sec)
🎤 **Speaking Time:** `{stats['speaking_time_min']} min`

🔤 **Longest Word:** `{stats['longest_word']}`
📊 **Avg Word Length:** `{stats['avg_word_length']} characters`
    """

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_message = f"""
👋 Hello {user.first_name}!

Welcome to **WordTallyX Bot**! 🎯

I can analyze any text you send me and provide detailed statistics:
• Word count
• Character count (with & without spaces)
• Sentence count
• Paragraph count
• Reading & speaking time
• Longest word
• Average word length

📤 **How to use:**
1. Send me any text message
2. I'll automatically analyze it
3. Get instant statistics!

💡 **Tip:** You can also forward articles, captions, or any text.

🔗 **Commands:**
/start - Show this message
/help - Get detailed help
/stats - Get stats for last analyzed text (coming soon)

Made with ❤️ by WordTallyX
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message when /help is issued."""
    help_text = """
📖 **How to use WordTallyX Bot**

Simply send me **any text** and I'll analyze it!

**What I analyze:**
✅ Words
✅ Characters (with and without spaces)
✅ Sentences
✅ Paragraphs
✅ Reading time
✅ Speaking time
✅ Longest word
✅ Average word length

**Example:**
Send: `The quick brown fox jumps over the lazy dog.`

I'll respond with a complete breakdown of that text!

**Commands:**
/start - Welcome message
/help - This help menu

**Privacy:** Your texts are processed and never stored.

Questions or suggestions? Feel free to reach out!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages and analyze them."""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Ignore commands
    if text.startswith('/'):
        return
    
    # Check if text is too short
    if len(text.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please send at least 3 characters for analysis!"
        )
        return
    
    # Show typing indicator
    await update.message.chat.send_action(action="typing")
    
    try:
        # Analyze the text
        stats = count_words(text)
        response = format_stats(stats)
        
        # Store last analysis for user
        user_sessions[user_id] = stats
        
        # Send response
        await update.message.reply_text(response, parse_mode="Markdown")
        
        # Add a tip
        if stats['word_count'] < 10:
            await update.message.reply_text(
                "💡 Send a longer text for more detailed analysis!"
            )
        elif stats['word_count'] > 500:
            await update.message.reply_text(
                "📚 Wow, that's a lot of text! Great for detailed analysis."
            )
            
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        await update.message.reply_text(
            "❌ Oops! Something went wrong. Please try again."
        )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show stats for last analyzed text."""
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text(
            "📭 You haven't analyzed any text yet. Send me some text first!"
        )
        return
    
    stats = user_sessions[user_id]
    response = format_stats(stats)
    await update.message.reply_text(
        f"📊 **Last Analysis**\n{response}",
        parse_mode="Markdown"
    )

# ============ MAIN FUNCTION ============

def main() -> None:
    """Start the bot."""
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Register message handler for text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Start the bot (polling)
    logger.info("Bot started! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
