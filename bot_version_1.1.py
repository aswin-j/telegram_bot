#!/usr/bin/env python

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image, ImageDraw, ImageFont
import os
import openai

# Bot Token: Use environment variable or fallback for testing
my_bot_token = os.getenv('YOUR_BOT_TOKEN', 'YOUR_DEFAULT_BOT_TOKEN')
if my_bot_token == 'YOUR_DEFAULT_BOT_TOKEN':
    raise RuntimeError("Bot token is missing. Set the 'YOUR_BOT_TOKEN' environment variable.")

# OpenAI API key for AI responses (if needed)
openai.api_key = os.getenv('OPENAI_API_KEY', 'YOUR_OPENAI_API_KEY')

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Study materials dictionary (path to resources)
study_materials = {
    "thermodynamics": "/path/to/thermodynamics.pdf",
    "data_structures": "/path/to/data_structures.pdf",
    "algorithms": "/path/to/algorithms.pdf",
}

# Start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message when the /start command is issued."""
    await update.message.reply_text(
        "Hi! I'm your Study Guide Bot. Here's what I can do:\n"
        "- Clear your doubts about topics.\n"
        "- Share study materials.\n\n"
        "Use /help for detailed instructions."
    )

# Help command handler
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a detailed help message when the /help command is issued."""
    await update.message.reply_text(
        "Here's how to use the bot:\n"
        "- Ask me any question, and I'll try to answer it.\n"
        "- Use /get_notes [subject] to request study materials.\n"
        "- For a list of available subjects, type /subjects."
    )

# List available subjects
async def subjects(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all available subjects for study materials."""
    subject_list = "\n".join(f"- {subject}" for subject in study_materials.keys())
    await update.message.reply_text(f"Available subjects:\n{subject_list}")

# Share study materials
async def get_notes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Share requested study materials."""
    if not context.args:
        await update.message.reply_text("Please specify a subject. Example: /get_notes thermodynamics")
        return

    subject = " ".join(context.args).lower()
    if subject in study_materials:
        file_path = study_materials[subject]
        with open(file_path, 'rb') as file:
            await update.message.reply_document(document=file, caption=f"Here is the {subject} material.")
    else:
        await update.message.reply_text(f"Sorry, I don't have materials for '{subject}'. Use /subjects to see available topics.")

# Handle doubts and questions
async def handle_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Try to resolve doubts using AI or predefined responses."""
    query = update.message.text

    # Predefined responses
    predefined_answers = {
        "what is thermodynamics": "Thermodynamics is the branch of physics concerned with heat and temperature and their relation to energy and work.",
        "what is data structures": "Data structures are ways of organizing and storing data efficiently for various operations."
    }

    # Check predefined responses first
    response = predefined_answers.get(query.lower())

    # If no predefined response, use OpenAI GPT for AI-powered response
    if not response:
        try:
            ai_response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"Answer the following query:\n{query}",
                max_tokens=100
            )
            response = ai_response['choices'][0]['text'].strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            response = "Sorry, I couldn't process your question. Please try again."

    await update.message.reply_text(response)

# Main function to run the bot
def main() -> None:
    """Start the bot."""
    # Create the application and pass the bot's token
    application = Application.builder().token(my_bot_token).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("subjects", subjects))
    application.add_handler(CommandHandler("get_notes", get_notes))

    # Add a message handler for general questions
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_query))

    # Run the bot until manually stopped
    application.run_polling()

if __name__ == "__main__":
    main()
