from discord import Interaction, VoiceChannel
from discord.app_commands import Choice, Group, command, describe, choices, rename
from structlog import get_logger

from src.models import AudioEffect
from src.services.audio import AudioService
from src.services.speak import SpeakService
from src.settings import audios


AUDIOS = {
    audio.title: audio
    for audio in vars(audios).values()
    if isinstance(audio, AudioEffect)
}

AUDIOS_CHOICES = [
    Choice(name=audio, value=audio)
    for audio in AUDIOS.keys()
]


class AudiosCommands(Group):

    def __init__(
        self,
        audio: AudioService,
        speak: SpeakService
    ):
        self.audio = audio
        self.speak_service = speak
        self.logger = get_logger()
        super().__init__(
            name='audio',
            description='Toque efeitos sonoros nas salas de voz'
        )


    @command(name="tocar", description="Toca um efeito sonoro na sala de voz")
    @rename(channel="canal")
    @describe(channel="Destino da mensagem")
    @rename(audio="áudio")
    @describe(audio="O efeito sonoro será tocado no canal")
    @choices(audio=AUDIOS_CHOICES)
    async def play(
        self,
        interaction: Interaction,
        channel: VoiceChannel,
        audio: Choice[str],
    ):
        self.logger.info(
            f"Pedindo para tocar efeito sonoro...",
            user=interaction.user.name,
            audio=audio.value,
            channel=channel.name,
        )

        try:
            await interaction.response.defer(ephemeral=True)

            if 'lobby' not in channel.name.lower():
                await interaction.edit_original_response(content="🔴 Só é possível tocar em um **lobby**!")
                return
            
            if len(channel.members) < 1:
                await interaction.edit_original_response(content="🔴 O canal precisa ter pelo menos **uma pessoa** conectada!")
                return

            await interaction.edit_original_response(
                content=f"⏳ Tocando ``{audio.value}`` em {channel.mention}..."
            )
            await self.audio.play(
                channel=channel,
                filename=AUDIOS[audio.value].filename
            )
            await interaction.edit_original_response(
                content=f"✅ Efeito sonoro ``{audio.value}`` tocado com sucesso em {channel.mention}!"
            )
            
            self.logger.info(
                f"Efeito sonoro tocado com sucesso!",
                user=interaction.user.name,
                channel=channel.name,
                audio=audio.value
            )

        except Exception as exc:
            await interaction.edit_original_response(
                content="🔴 Ocorreu um erro ao tentar tocar o efeito sonoro."
            )
            self.logger.error(
                f"Erro ao tentar tocar efeito sonoro!",
                user=interaction.user.name,
                channel=channel.name,
                audio=audio.value,
                error=str(exc)
            )

    @command(name="falar", description="Mande uma mensagem para um canal de voz")
    @rename(channel="canal")
    @describe(channel="Destino da mensagem")
    @rename(message="mensagem")
    @describe(message="Esta mensagem será falada (lida pelo bot) no canal de voz")
    async def speak(
        self,
        interaction: Interaction,
        channel: VoiceChannel,
        message: str,
    ):
        self.logger.info(
            f"Enviando mensagem para sala de voz...",
            user=interaction.user.name,
            channel=channel.name,
            message=message
        )

        try:
            await interaction.response.defer(ephemeral=True)

            if 'lobby' not in channel.name.lower():
                await interaction.edit_original_response(content="🔴 Só é possível falar em um **lobby**!")
                return

            if len(channel.members) < 1:
                await interaction.edit_original_response(content="🔴 O canal precisa ter pelo menos **uma pessoa** conectada!")
                return

            if len(message) < 1:
                await interaction.edit_original_response(content="🔴 A mensagem não pode estar vazia!")
                return

            if len(message) > 100:
                await interaction.edit_original_response(content="🔴 A mensagem não pode ter mais de **100 caracteres**!")
                return

            await interaction.edit_original_response(
                content=f"⏳ Falando em {channel.mention}..."
            )
            await self.audio.play(
                channel=channel,
                filename=await self.speak_service.write(message)
            )
            await self.speak_service.clean()
            await interaction.edit_original_response(
                content=f"✅ Mensagem falada com sucesso em {channel.mention}!"
            )

            self.logger.info(
                f"Mensagem falada com sucesso!",
                user=interaction.user.name,
                channel=channel.name,
                message=message
            )

        except Exception as exc:
            await interaction.edit_original_response(
                content="🔴 Ocorreu um erro ao tentar falar na sala de voz."
            )
            self.logger.error(
                f"Erro ao tentar falar na sala de voz!",
                user=interaction.user.name,
                channel=channel.name,
                message=message,
                error=str(exc)
            )
