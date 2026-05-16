from functools import cached_property, lru_cache

from discord import Client, Intents, Object, Message, VoiceChannel, TextChannel
from discord.abc import GuildChannel
from discord.app_commands import CommandTree
from pyportainer import Portainer
from structlog import get_logger

from src.services.portainer import PortainerService
from src.commands.general import GeneralCommands
from src.commands.minecraft import MinecraftCommands
from src.settings import (
    DISCORD_GUILD_ID,
    DISCORD_MESSAGES_CHANNEL_ID,
    DISCORD_MUSIC_CHANNEL_ID,
    PORTAINER_API_KEY,
    PORTAINER_API_URL
)

portainer = Portainer(
    api_url=PORTAINER_API_URL,
    api_key=PORTAINER_API_KEY
)


class CleitonRasta(Client):
    guild = Object(DISCORD_GUILD_ID)
    logger = get_logger()

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
            guild=self.guild,
        )
        _tree.add_command(
            MinecraftCommands(
                portainer_service=PortainerService(portainer),
            ),
            guild=self.guild,
        )
        return _tree

    async def setup_hook(self) -> None:
        self.logger.info("Sincronizando comandos do bot...")
        await self.tree.sync(guild=self.guild)

    async def on_message(self, message: Message):
        if message.author.bot:
            return
        if isinstance(message.channel, VoiceChannel):
            self.logger.info(
                "Mensagem enviada em canal de voz, apagando mensagem...",
                channel=message.channel.name,
                user=message.author.name,
                message=message.content
            )
            await message.delete()
    
    async def on_guild_channel_create(self, channel: GuildChannel):
        if isinstance(channel, VoiceChannel):
            self.logger.info(
                "Canal de voz criado, enviando mensagem de aviso...",
                channel=channel.name
            )
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
