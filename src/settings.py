from datetime import timezone
from os import getenv


TIMEZONE = timezone.utc

DISCORD_TOKEN = getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = int(getenv("DISCORD_GUILD_ID", "0"))
DISCORD_ADMIN_ROLE_ID = int(getenv("DISCORD_ADMIN_ROLE_ID", "0"))
DISCORD_MINECRAFT_CHANNEL_ID = int(getenv("DISCORD_MINECRAFT_CHANNEL_ID", "0"))

OCI_MACHINE_ID = getenv("OCI_MACHINE_ID", "")

MINECRAFT_RCON_HOST = getenv("MINECRAFT_RCON_HOST", "localhost")
MINECRAFT_RCON_PORT = int(getenv("MINECRAFT_RCON_PORT", "25575"))
MINECRAFT_RCON_PASSWORD = getenv("MINECRAFT_RCON_PASSWORD", "minedoscrazy")
