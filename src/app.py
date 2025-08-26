from functools import cached_property, lru_cache

from discord import Client, Intents, Object
from discord.app_commands import CommandTree

from src.integrations.rcon import RconIntegration
from src.integrations.oracle import OracleIntegration
from src.commands.minecraft import MinecraftCommands
from src.settings import DISCORD_GUILD_ID, MACHINE_ID


class CleitonRasta(Client):
    guild = Object(DISCORD_GUILD_ID)    

    @cached_property
    def tree(self):
        _tree = CommandTree(self)
        _tree.add_command(
            MinecraftCommands(
                OracleIntegration(MACHINE_ID),
                RconIntegration('minedoscrazy', 'localhost', 25575)
            ),
            guild=self.guild
        )
        return _tree

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=self.guild)


@lru_cache
def get_bot() -> CleitonRasta:
    return CleitonRasta(intents=Intents.default())
