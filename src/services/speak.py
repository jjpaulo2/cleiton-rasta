from asyncio import to_thread
from pathlib import Path

from gtts import gTTS


class SpeakService:

    def __init__(self):
        self.output_filename = Path("/tmp/gtts.mp3")

    async def write(self, message: str) -> str:
        tts = gTTS(text=message, lang='pt', tld='com.br')
        await to_thread(tts.save, self.output_filename)
        return str(self.output_filename)

    async def clean(self):
        if self.output_filename.exists():
            await to_thread(self.output_filename.unlink)
