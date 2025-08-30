from functools import cached_property, lru_cache

from discord import Client, Intents, Object
from discord.app_commands import CommandTree

from src.commands.minecraft import MinecraftCommands
from src.loaders.oracle_auth import OracleAuthLoader
from src.integrations.rcon import RconIntegration
from src.integrations.oracle import OracleIntegration
from src.settings import (
    OCI_MACHINE_ID,
    MINECRAFT_DOMAIN_NAME,
    MINECRAFT_RCON_PASSWORD,
    MINECRAFT_RCON_PORT,
    DISCORD_GUILD_ID
)


oracle_integration = OracleIntegration(
    machine_id=OCI_MACHINE_ID,
    auth=OracleAuthLoader()
)

rcon_integration = RconIntegration(
    password=MINECRAFT_RCON_PASSWORD,
    host=MINECRAFT_DOMAIN_NAME,
    port=MINECRAFT_RCON_PORT
)


class CleitonRasta(Client):
    guild = Object(DISCORD_GUILD_ID)

    @cached_property
    def tree(self):
        _tree = CommandTree(self)
        _tree.add_command(
            MinecraftCommands(
                oracle=oracle_integration,
                rcon=rcon_integration
            ),
            guild=self.guild
        )
        return _tree

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=self.guild)


@lru_cache
def get_bot() -> CleitonRasta:
    return CleitonRasta(intents=Intents.default())
