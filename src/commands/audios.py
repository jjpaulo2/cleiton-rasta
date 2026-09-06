from discord import Interaction, VoiceChannel
from discord.app_commands import Choice, Group, command, describe, choices, rename

from structlog import get_logger

from src.services.audio import AudioService


AUDIOS_CHOICES = [
    Choice(name="🗿 Ooooh StoneMask...", value="stonemask.mp3"),
    Choice(name="👹 Baphomet!", value="baphomet.mp3"),
    Choice(name="🐐 Bééé...", value="bode.mp3"),
]


class AudiosCommands(Group):

    def __init__(
        self,
        audio: AudioService,
    ):
        self.audio = audio
        self.logger = get_logger()
        super().__init__(
            name='audios',
            description='Toque efeitos sonoros nas salas de voz'
        )


    @command(name="tocar", description="Toca um efeito sonoro na sala de voz")
    @rename(audio="áudio")
    @rename(channel="canal")
    @describe(audio="Selecione o efeito sonoro que deseja tocar.")
    @choices(audio=AUDIOS_CHOICES)
    async def play(
        self,
        interaction: Interaction,
        audio: Choice[str],
        channel: VoiceChannel,
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
                filename=audio.value
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

        except Exception as e:
            self.logger.error(
                f"Erro ao tentar tocar efeito sonoro!",
                user=interaction.user.name,
                channel=channel.name,
                audio=audio.value,
                error=str(e)
            )
            await interaction.edit_original_response(
                content="🔴 Ocorreu um erro ao tentar tocar o efeito sonoro."
            )
