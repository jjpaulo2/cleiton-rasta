from src.models import GameServer
from src.settings.nodes import HEAVY_NODE


MINECRAFT = GameServer(
    name='Minecraft',
    container_names=[
        'minecraft-loggifly-1',
        'minecraft-minecraft-1'
    ],
    node=HEAVY_NODE,
)

CORE_KEEPER = GameServer(
    name='Core Keeper',
    container_names=[
        'core-keeper-server-1'
    ],
    node=HEAVY_NODE,
)
