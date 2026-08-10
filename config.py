import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

BOT_NAME = "C0RE"
BOT_VERSION = "1.0.0"

PREFIX = ">"