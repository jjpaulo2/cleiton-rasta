from asyncio import sleep

from discord import (
    Client,
    Intents,
    Object,
    Message,
    VoiceChannel,
    Member,
    VoiceState,
    FFmpegPCMAudio,
    ClientException
)
from discord.abc import GuildChannel
from discord.app_commands import CommandTree
from structlog import get_logger

from src.services.portainer import PortainerService
from src.services.audio import AudioService
from src.commands.servers import ServersCommands
from src.settings.common import DISCORD_GUILD_ID


logger = get_logger()
guild = Object(DISCORD_GUILD_ID)
client = Client(intents=Intents.default())

audio = AudioService(logger)
portainer = PortainerService()

tree = CommandTree(client)
tree.add_command(
    ServersCommands(portainer),
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


@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if before.channel:
        return
    if 'lobby' not in after.channel.name.lower():
        return
    if member.guild and member.guild.voice_client:
        return
    if 'baphomet' in member.display_name.lower():
        await audio.play(after.channel, "baphomet.mp3")
    if 'stone' in member.display_name.lower() and len(after.channel.members) > 1:
        await audio.play(after.channel, "stonemask.mp3")
