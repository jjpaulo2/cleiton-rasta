from src.app import get_bot
from src.settings import DISCORD_TOKEN


if __name__ == '__main__':
    get_bot().run(DISCORD_TOKEN)
