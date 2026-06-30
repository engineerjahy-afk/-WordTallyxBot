import os
import re
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("BOT_TOKEN environment variable not set!")
    raise ValueError("BOT_TOKEN environment variable not set!")

# Dictionary to store user sessions
user_sessions = {}

# ============ HELPER FUNCTIONS ============

def count_words(text: str) -> dict:
    """
    Count words, characters, sentences, paragraphs, and reading time.
    """
    # Word count - find all words
    words = re.findall(r"\b\w+\b", text)
    word_count = len(words)
    
    # Character count
    char_count = len(text)
    char_count_no_spaces = len(text.replace(" ", ""))
    char_count_no_punctuation = len(re.sub(r'[^\w\s]', '', text))
    
    # Sentence count - split by ., !, ?
    sentences = re.split(r'[.!?]+', text)
    sentence_count = len([s for s in sentences if s.strip()])
    
    # Paragraph count - split by newlines
    paragraphs = [p for p in text.split('\n') if p.strip()]
    paragraph_count = len(paragraphs)
    
    # Reading time (average 200 words per minute)
    reading_time_min = word_count / 200 if word_count > 0 else 0
    reading_time_sec = reading_time_min * 60
    
    # Speaking time (average 150 words per minute)
    speaking_time_min = word_count / 150 if word_count > 0 else 0
    
    # Longest word
    longest_word = max(words, key=len) if words else "None"
    longest_word_length = len(longest_word) if longest_word != "None" else 0
    
    # Shortest word
    shortest_word = min(words, key=len) if words else "None"
    shortest_word_length = len(shortest_word) if shortest_word != "None" else 0
    
    # Average word length
    avg_word_length = sum(len(w) for w in words) / word_count if word_count > 0 else 0
    
    # Count unique words
    unique_words = len(set(words))
    
    return {
        "word_count": word_count,
        "char_count": char_count,
        "char_count_no_spaces": char_count_no_spaces,
        "char_count_no_punctuation": char_count_no_punctuation,
        "sentence_count": sentence_count,
        "paragraph_count": paragraph_count,
        "reading_time_min": round(reading_time_min, 1),
        "reading_time_sec": round(reading_time_sec, 0),
        "speaking_time_min": round(speaking_time_min, 1),
        "longest_word": longest_word,
        "longest_word_length": longest_word_length,
        "shortest_word": shortest_word,
        "shortest_word_length": shortest_word_length,
        "avg_word_length": round(avg_word_length, 1),
        "unique_words": unique_words,
    }

def format_stats(stats: dict) -> str:
    """
    Format statistics into a readable message.
    """
    return f"""
📊 **Text Statistics**

📝 **Words:** `{stats['word_count']}`
🔤 **Unique Words:** `{stats['unique_words']}`
✏️ **Characters (with spaces):** `{stats['char_count']}`
📏 **Characters (no spaces):** `{stats['char_count_no_spaces']}`
📌 **Characters (no punctuation):** `{stats['char_count_no_punctuation']}`
📄 **Sentences:** `{stats['sentence_count']}`
📑 **Paragraphs:** `{stats['paragraph_count']}`

⏱️ **Reading Time:** `{stats['reading_time_min']} min` ({stats['reading_time_sec']} sec)
🎤 **Speaking Time:** `{stats['speaking_time_min']} min`

🔤 **Longest Word:** `{stats['longest_word']}` ({stats['longest_word_length']} chars)
📝 **Shortest Word:** `{stats['shortest_word']}` ({stats['shortest_word_length']} chars)
📊 **Avg Word Length:** `{stats['avg_word_length']} characters`
    """

# ============ COMMAND HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send a welcome message when /start is issued.
    """
    user = update.effective_user
    welcome_message = f"""
👋 Hello {user.first_name}!

Welcome to **WordTallyX Bot**! 🎯

I'm your personal text analysis assistant. Send me any text and I'll provide detailed statistics.

📊 **What I analyze:**
• Word count
• Unique words
• Character count (with & without spaces)
• Sentence count
• Paragraph count
• Reading & speaking time
• Longest & shortest word
• Average word length

📤 **How to use:**
Simply send me any text message and I'll analyze it instantly!

💡 **Tips:**
• Forward articles, captions, or any text
• Longer texts get more detailed analysis
• Use /stats to see your last analysis

🔗 **Commands:**
/start - Show this welcome message
/help - Get detailed help
/stats - Show your last analysis
/about - About this bot

Made with ❤️ by WordTallyX
    """
    await update.message.reply_text(welcome_message, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send help message when /help is issued.
    """
    help_text = """
📖 **How to use WordTallyX Bot**

**Simple Usage:**
1. Send me any text message
2. I'll analyze it automatically
3. Get detailed statistics instantly!

**What I analyze:**
✅ Words (total and unique)
✅ Characters (with/without spaces/punctuation)
✅ Sentences
✅ Paragraphs
✅ Reading time (based on 200 wpm)
✅ Speaking time (based on 150 wpm)
✅ Longest and shortest word
✅ Average word length

**Commands:**
/start - Welcome message
/help - This help menu
/stats - Show your last analysis
/about - About this bot

**Example:**
Send: `The quick brown fox jumps over the lazy dog.`

I'll respond with a complete breakdown!

**Privacy:** Your texts are processed and never stored permanently.

**Questions or suggestions?** Feel free to reach out!
    """
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Send about message when /about is issued.
    """
    about_text = """
🤖 **About WordTallyX Bot**

**Version:** 1.0.0
**Created:** 2026
**Language:** Python 3.11

**Features:**
• Real-time text analysis
• Detailed statistics
• Privacy-focused (no data stored)
• Fast and reliable

**Technologies:**
• python-telegram-bot
• Railway (hosting)
• GitHub (source control)

**Why WordTallyX?**
Perfect for writers, students, editors, and anyone who wants to understand their text better.

**Feedback:**
Your suggestions help improve this bot!
    """
    await update.message.reply_text(about_text, parse_mode="Markdown")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Show stats for the last analyzed text.
    """
    user_id = update.effective_user.id
    
    if user_id not in user_sessions:
        await update.message.reply_text(
            "📭 You haven't analyzed any text yet.\n\n"
            "Send me some text first and I'll analyze it for you!"
        )
        return
    
    stats = user_sessions[user_id]
    response = format_stats(stats)
    await update.message.reply_text(
        f"📊 **Your Last Analysis**\n{response}",
        parse_mode="Markdown"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle text messages and analyze them.
    """
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
    
    # Check if text is too long (Telegram limit is 4096 characters)
    if len(text) > 4096:
        await update.message.reply_text(
            "⚠️ Text is too long! Please send a shorter text (max 4096 characters)."
        )
        return
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Analyze the text
        stats = count_words(text)
        response = format_stats(stats)
        
        # Store last analysis for user
        user_sessions[user_id] = stats
        
        # Send response
        await update.message.reply_text(response, parse_mode="Markdown")
        
        # Add tips based on text length
        if stats['word_count'] < 10:
            await update.message.reply_text(
                "💡 **Tip:** Send a longer text (10+ words) for more detailed analysis!"
            )
        elif stats['word_count'] > 500:
            await update.message.reply_text(
                "📚 **Wow!** That's a lot of text. Great for detailed analysis. "
                f"Reading time: {stats['reading_time_min']} minutes."
            )
        elif stats['word_count'] > 100:
            await update.message.reply_text(
                f"✅ **Good length!** {stats['word_count']} words analyzed. "
                f"Average reading time: {stats['reading_time_min']} minutes."
            )
            
    except Exception as e:
        logger.error(f"Error analyzing text: {e}")
        await update.message.reply_text(
            "❌ Oops! Something went wrong while analyzing your text.\n\n"
            "Please try again or send a different text."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Log errors and send a message to the user.
    """
    logger.error(f"Update {update} caused error {context.error}")
    
    # Send a message to the user
    if update and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again later."
        )

# ============ MAIN FUNCTION ============

def main() -> None:
    """
    Start the bot.
    """
    try:
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Register command handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("stats", stats_command))
        
        # Register message handler for text (excluding commands)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # Register error handler
        application.add_error_handler(error_handler)
        
        # Start the bot (polling)
        logger.info("=" * 50)
        logger.info("🤖 WordTallyX Bot Started Successfully!")
        logger.info(f"🔑 Bot Token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
        logger.info("📡 Polling for updates...")
        logger.info("=" * 50)
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
