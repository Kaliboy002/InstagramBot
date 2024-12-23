import os
import instaloader
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext
from telegram.ext import filters

# Telegram Bot Token
TELEGRAM_TOKEN = "7080362550:AAEgjuX2RQ-4T0OoZAFeFQrtl6pB110cTGA"

# Create an instance of Instaloader
L = instaloader.Instaloader()

# Download Instagram story from link
def download_story(url: str, chat_id: int, context: CallbackContext):
    try:
        # Extract the username from the URL
        shortcode = url.split('/')[-2]
        
        # Check if the URL is a valid Instagram link
        if not shortcode:
            return "Invalid Instagram URL!"

        # Try to load the profile
        profile = instaloader.Profile.from_username(L.context, shortcode)
        
        # Download all stories of the profile
        stories = L.get_stories(userids=[profile.userid])
        download_path = f"downloads/{profile.username}"
        
        # Make a folder to store the downloaded content
        os.makedirs(download_path, exist_ok=True)

        for story in stories:
            for item in story.get_items():
                L.download_storyitem(item, target=download_path)

        # Send success message to Telegram chat
        message = "The story has been successfully downloaded."
        
        # Send the story as a file
        for story_file in os.listdir(download_path):
            if story_file.endswith('.mp4') or story_file.endswith('.jpg'):
                with open(f'{download_path}/{story_file}', 'rb') as f:
                    context.bot.send_document(chat_id=chat_id, document=f)

        # Clean up downloaded files
        for story_file in os.listdir(download_path):
            os.remove(f'{download_path}/{story_file}')
        os.rmdir(download_path)
        
        return message
    except Exception as e:
        return f"Failed to download story: {e}"

# Start command for the Telegram bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Send me the Instagram story link, and I will download it for you!')

# Handle incoming links and download stories
async def handle_message(update: Update, context: CallbackContext):
    url = update.message.text
    if "instagram.com" in url:
        message = download_story(url, update.message.chat_id, context)
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("Please send a valid Instagram story URL.")

# Main function to start the bot
def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add command and message handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
