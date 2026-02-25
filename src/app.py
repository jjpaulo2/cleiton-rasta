from functools import cached_property, lru_cache

from discord import Client, Intents, Object, Message, VoiceChannel, TextChannel
from discord.abc import GuildChannel
from discord.app_commands import CommandTree

from src.commands.general import GeneralCommands
from src.commands.minecraft import MinecraftCommands
from src.loaders.oracle_auth import OracleAuthLoader
from src.integrations.oracle import OracleIntegration
from src.settings import (
    OCI_MACHINE_ID,
    DISCORD_GUILD_ID,
    DISCORD_MESSAGES_CHANNEL_ID,
    DISCORD_MUSIC_CHANNEL_ID
)


oracle_integration = OracleIntegration(
    machine_id=OCI_MACHINE_ID,
    auth=OracleAuthLoader()
)


class CleitonRasta(Client):
    guild = Object(DISCORD_GUILD_ID)

    @cached_property
    def messages_channel(self) -> TextChannel:
        channel = self.get_channel(DISCORD_MESSAGES_CHANNEL_ID)
        if not isinstance(channel, TextChannel):
            raise ValueError("O canal de mensagens deve ser um canal de texto.")
        return channel

    @cached_property
    def music_channel(self) -> TextChannel:
        channel = self.get_channel(DISCORD_MUSIC_CHANNEL_ID)
        if not isinstance(channel, TextChannel):
            raise ValueError("O canal de música deve ser um canal de texto.")
        return channel

    @cached_property
    def tree(self):
        _tree = CommandTree(self)
        _tree.add_command(
            GeneralCommands(),
            guild=self.guild
        )
        _tree.add_command(
            MinecraftCommands(
                oracle=oracle_integration
            ),
            guild=self.guild
        )
        return _tree

    async def setup_hook(self) -> None:
        await self.tree.sync(guild=self.guild)

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, VoiceChannel):
            await message.delete()
    
    async def on_guild_channel_create(self, channel: GuildChannel):
        if isinstance(channel, VoiceChannel):
            await channel.send(
                content=(
                    "Este chat não pode ser usado! "
                    "Qualquer mensagem enviada aqui será apagada imediatamente.\n\n"
                    f"- Use {self.music_channel.mention} para tocar música.\n"
                    f"- Use {self.messages_channel.mention} para conversar."
                ),
                silent=True
            )


@lru_cache
def get_bot() -> CleitonRasta:
    return CleitonRasta(intents=Intents.default())
