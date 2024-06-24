import os

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN") 
AUTHOR_ID = int(os.getenv("DISCORD_USER_ID")) #for some reason the id from env is read as a string, so i had to turn to int.
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY")

