from discord import (
    Client,
    Intents,
    Object,
    Message,
    VoiceChannel,
    Member,
    VoiceState,
    opus
)
from discord.abc import GuildChannel
from discord.app_commands import CommandTree
from structlog import get_logger

from src.services.portainer import PortainerService
from src.services.audio import AudioService
from src.commands.servers import ServersCommands
from src.commands.audios import AudiosCommands
from src.settings.common import DISCORD_GUILD_ID
from src.utils import set_default_activity


logger = get_logger()
guild = Object(DISCORD_GUILD_ID)
client = Client(intents=Intents.default())

audio = AudioService()
portainer = PortainerService()

tree = CommandTree(client)
tree.add_command(
    ServersCommands(portainer),
    guild=guild,
)
tree.add_command(
    AudiosCommands(audio),
    guild=guild,
)


@client.event
async def on_ready():
    logger.info("Bot conectado com sucesso!")
    await tree.sync(guild=guild)
    logger.info("Comandos sincronizados com sucesso!")
    try:
        if not opus.is_loaded():
            opus.load_opus("/usr/lib/libopus.so.0")
            logger.info("Libopus carregado com sucesso!")
    except Exception as exc:
        logger.error("Erro ao carregar o libopus!", error=str(exc))
    await set_default_activity(client)


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
    if len(after.channel.members) <= 1:
        return
    if 'baphomet' in member.display_name.lower():
        await audio.play(after.channel, "baphomet.mp3")
    if 'stone' in member.display_name.lower():
        await audio.play(after.channel, "stonemask.mp3")
    if 'bode' in member.display_name.lower():
        await audio.play(after.channel, "bode.mp3")
