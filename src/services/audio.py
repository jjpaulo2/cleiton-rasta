from asyncio import run
from discord import VoiceChannel, FFmpegPCMAudio, PCMVolumeTransformer, ClientException
from src.settings.common import AUDIOS_FOLDER


class AudioService:

    def __init__(self, logger):
        self.logger = logger

    def _get_audio_file(self, filename: str) -> str:
        audio = AUDIOS_FOLDER / filename
        if not audio.exists():
            raise FileNotFoundError(f"Audio file '{filename}' not found in '{AUDIOS_FOLDER}'.")
        return str(audio)

    async def play(self, channel: VoiceChannel, filename: str):
        try:
            voice = await channel.connect()
            audio = FFmpegPCMAudio(self._get_audio_file(filename))
            audio = PCMVolumeTransformer(audio, volume=0.15)
            voice.play(audio, after=lambda e: run(voice.disconnect()))

        except ClientException as exc:
            self.logger.error(
                "Erro ao reproduzir áudio no canal de voz.",
                error=str(exc),
                channel=channel.name,
            )
