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
from src.services.speak import SpeakService
from src.services.profile import ProfileService
from src.commands.audios import AudiosCommands
from src.commands.profiles import ProfilesCommands
from src.commands.servers import ServersCommands
from src.settings.common import DISCORD_GUILD_ID
from src.settings.actions import NICKNAMES_TO_TRIGGER_AUDIO


logger = get_logger()
guild = Object(DISCORD_GUILD_ID)
client = Client(intents=Intents.default())

audio = AudioService()
speak = SpeakService()
portainer = PortainerService()
profile = ProfileService(client, DISCORD_GUILD_ID)

tree = CommandTree(client)
tree.add_command(
    ServersCommands(portainer, profile),
    guild=guild,
)
tree.add_command(
    AudiosCommands(audio, speak),
    guild=guild,
)
tree.add_command(
    ProfilesCommands(profile),
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
    await profile.set_default_presence() 


@client.event
async def on_message(message: Message):
    if message.guild and message.guild.me.id == message.author.id:
        return
    if client.user in message.mentions:
        await message.reply("Vai tomar no cu!")
        return
    if isinstance(message.channel, VoiceChannel):
        logger.info(
            "Mensagem enviada em canal de voz, apagando mensagem...",
            channel=message.channel.name,
            user=message.author.name,
            message=message.content
        )
        await message.delete()
        if not message.author.bot:
            await message.channel.send(
                content=(f"{message.author.mention} você não pode enviar mensagens aqui!"),
                silent=True
            )


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
    for nick, audio_effect in NICKNAMES_TO_TRIGGER_AUDIO.items():
        if nick in member.display_name.lower():
            await audio.play(after.channel, audio_effect.filename)
            return
