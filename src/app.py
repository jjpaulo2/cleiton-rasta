from functools import cached_property

from discord import Client, Intents, Object
from discord.app_commands import CommandTree

from src.integrations.minedoscrazy import MineDosCrazy
from src.commands.minecraft import MinecraftCommands
from src.settings import DISCORD_GUILD_ID, MACHINE_ID


class CleitonRasta(Client):
    guild = Object(DISCORD_GUILD_ID)    

    @cached_property
    def tree(self):
        _tree = CommandTree(self)
        _tree.add_command(
            MinecraftCommands(
                MineDosCrazy(MACHINE_ID)
            ),
            guild=self.guild
        )
        return _tree

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=self.guild)


intents = Intents.default()
client = CleitonRasta(intents=intents)
