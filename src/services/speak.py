from asyncio import to_thread

from structlog import get_logger
from gtts import gTTS

from src.settings.common import AUDIOS_FOLDER


class SpeakService:

    def __init__(self):
        self.output_filename = AUDIOS_FOLDER / "gtts.mp3"

    async def write(self, message: str) -> str:
        tts = gTTS(text=message, lang='pt', tld='com.br')
        await to_thread(tts.save, self.output_filename)
        return self.output_filename.name

    async def clean(self):
        if self.output_filename.exists():
            await to_thread(self.output_filename.unlink)
