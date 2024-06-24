
#RESTART PC AFTER CHANGING ANY ENVIUROMENTAL ID, IDK WHY BUT IT WORKS.
import os

token = os.getenv("DISCORD_BOT_TOKEN")
print(f"Loaded token: {token}")


author = os.getenv("DISCORD_USER_ID")
print(f"Author ID: {author}")

