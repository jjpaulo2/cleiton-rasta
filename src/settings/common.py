from os import getenv
from pathlib import Path


DISCORD_TOKEN = getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = int(getenv("DISCORD_GUILD_ID", "0"))
DISCORD_NOTIFICATIONS_CHANNEL_ID = int(getenv("DISCORD_NOTIFICATIONS_CHANNEL_ID", "0"))

PORTAINER_API_URL = getenv("PORTAINER_API_URL", "")
PORTAINER_API_KEY = getenv("PORTAINER_API_KEY", "")

AUDIOS_FOLDER = Path(__file__).parent.parent / "static" / "audio"
