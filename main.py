from textcommands import client
from Tokens import *


#starts bot
if DISCORD_BOT_TOKEN:
    client.run(DISCORD_BOT_TOKEN)
else:
    print("Error: No token provided. Set the DISCORD_BOT_TOKEN environment variable.")