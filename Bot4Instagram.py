import telebot
from instagrapi import Client
import pyshorteners
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("7080362550:AAEgjuX2RQ-4T0OoZAFeFQrtl6pB110cTGA")
INSTA_USER = os.getenv("73j3")
INSTA_PASS = os.getenv("nrkrk")

# Initialize bot and Instagram client
bot = telebot.TeleBot(BOT_TOKEN)
cl = Client()
cl.login(INSTA_USER, INSTA_PASS)
type_tiny = pyshorteners.Shortener()

# Welcome message
@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(
        message,
        "Welcome!\nYou can download Instagram content (Stories, Posts, Reels, IGTV, Profile Pictures).\n\n"
        "To get a user's profile picture, type:\n`:username`\n\n"
        "To download media, just send the Instagram URL."
    )

# Media downloader handler
@bot.message_handler(func=lambda msg: True)
def download(message):
    txt = message.text.strip()
    res = "Unavailable link or invalid input."
    
    try:
        # Handle Instagram URLs
        if 'instagram.com' in txt:
            if 'stories' in txt:
                # Download Story
                try:
                    story_pk = cl.story_pk_from_url(txt)
                    story = cl.story_info(story_pk).dict()
                    if story.get('video_url'):
                        res = type_tiny.tinyurl.short(story['video_url'])
                    elif story.get('thumbnail_url'):
                        res = type_tiny.tinyurl.short(story['thumbnail_url'])
                except Exception:
                    res = "Failed to download the story. Ensure the link is correct."

            elif any(segment in txt for segment in ['/p/', '/tv/', '/reel/']):
                # Download Post/Reel/IGTV
                try:
                    media_pk = cl.media_pk_from_url(txt)
                    media_info = cl.media_info(media_pk).dict()
                    media_type = media_info.get('media_type')
                    
                    if media_type == 2:  # Video
                        res = type_tiny.tinyurl.short(media_info['video_url'])
                    elif media_type == 1:  # Image
                        res = type_tiny.tinyurl.short(media_info['thumbnail_url'])
                    elif media_type == 8:  # Album
                        res = "Album content:\n"
                        for item in media_info['resources']:
                            url = item.get('video_url') or item.get('thumbnail_url')
                            if url:
                                res += type_tiny.tinyurl.short(url) + "\n"
                except Exception:
                    res = "Failed to download the media. Ensure the link is correct."

        # Handle profile picture download
        elif txt.startswith(':'):
            username = txt[1:].strip()
            try:
                user_info = cl.user_info_by_username(username).dict()
                res = type_tiny.tinyurl.short(user_info['profile_pic_url'])
            except Exception:
                res = "User not found or account is private."

        # Default error message
        else:
            res = "Invalid input. Please send a valid Instagram URL or `:username`."
    
    except Exception as e:
        res = f"An error occurred: {str(e)}"

    # Send the result
    bot.send_message(chat_id=message.chat.id, text=res)

# Start polling
bot.infinity_polling()
