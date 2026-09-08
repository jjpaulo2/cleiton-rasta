from asyncio import get_running_loop, run_coroutine_threadsafe, sleep

from discord import VoiceChannel, FFmpegPCMAudio, PCMVolumeTransformer, ClientException, VoiceClient
from structlog import get_logger

from src.settings.common import AUDIOS_FOLDER


class AudioService:

    def __init__(self):
        self.logger = get_logger()

    def _get_audio_file(self, filename: str) -> str:
        audio = AUDIOS_FOLDER / filename
        if not audio.exists():
            raise FileNotFoundError(f"Audio file '{filename}' not found in '{AUDIOS_FOLDER}'.")
        return str(audio)

    async def _disconnect(self, voice: VoiceClient):
        await sleep(0.5)
        await voice.disconnect()
        voice.cleanup()

    async def play(self, channel: VoiceChannel, filename: str):
        self.logger.info("Tocando áudio...", audio=filename, channel=channel.name)

        try:
            if voice := channel.guild.voice_client:
                await self._disconnect(voice)
            
            voice = await channel.connect()
            audio = FFmpegPCMAudio(self._get_audio_file(filename))
            audio = PCMVolumeTransformer(audio, volume=0.5)
            audio.read()
            await sleep(0.5)
            loop = get_running_loop()
            voice.play(audio, after=lambda _: run_coroutine_threadsafe(
                coro=self._disconnect(voice),
                loop=loop,
            ))

        except ClientException as exc:
            self.logger.error(
                "Erro ao reproduzir áudio no canal de voz.",
                error=str(exc),
                channel=channel.name,
            )
