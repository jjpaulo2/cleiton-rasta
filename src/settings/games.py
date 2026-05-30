from src.models import GameServer
from src.settings.nodes import HEAVY_NODE


MINECRAFT = GameServer(
    name='Minecraft',
    container_names=['minecraft-minecraft-1'],
    node=HEAVY_NODE,
)
