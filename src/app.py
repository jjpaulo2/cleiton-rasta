from discord import Client, Intents, Object, Message, VoiceChannel
from discord.abc import GuildChannel
from discord.app_commands import CommandTree
from structlog import get_logger

from src.services.portainer import PortainerService
from src.commands.servers import ServersCommands
from src.settings.common import DISCORD_GUILD_ID


logger = get_logger()
guild = Object(DISCORD_GUILD_ID)
client = Client(intents=Intents.default())

tree = CommandTree(client)
tree.add_command(
    ServersCommands(PortainerService()),
    guild=guild,
)


@client.event
async def on_ready():
    logger.info("Bot conectado com sucesso!")
    await tree.sync(guild=guild)
    logger.info("Comandos sincronizados com sucesso!")


@client.event
async def on_message(message: Message):
    if message.author.bot:
        return
    if isinstance(message.channel, VoiceChannel):
        logger.info(
            "Mensagem enviada em canal de voz, apagando mensagem...",
            channel=message.channel.name,
            user=message.author.name,
            message=message.content
        )
        await message.delete()


@client.event
async def on_guild_channel_create(channel: GuildChannel):
    if isinstance(channel, VoiceChannel):
        logger.info(
            "Canal de voz criado, enviando mensagem de aviso...",
            channel=channel.name
        )
        await channel.send(
            content=(
                "Este chat não pode ser usado! "
                "Qualquer mensagem enviada aqui será apagada imediatamente."
            ),
            silent=True
        )
