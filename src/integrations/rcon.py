import asyncio

from functools import cached_property
from mcrcon import MCRcon


class RconIntegration:

    def __init__(
        self,
        password: str,
        host: str | None = None,
        port: int | None = None
    ):
        self.password = password
        self.host = host or 'localhost'
        self.port = port or 25575

    @cached_property
    def client(self):
        return MCRcon(self.host, self.password, self.port)

    async def _connect(self):
        await asyncio.to_thread(self.client.connect)
    
    async def _disconnect(self):
        await asyncio.to_thread(self.client.disconnect)

    async def _command(self, command: str) -> str:
        return await asyncio.to_thread(self.client.command, command)

    async def is_ready(self) -> bool:
        ready = False
        try:
            await self._connect()
            ready = True
        except Exception:
            ready = False
        finally:
            await self._disconnect()
        return ready
    
    async def send_command(self, command: str) -> str:
        try:
            await self._connect()
            response = await self._command(command)
        finally:
            await self._disconnect()
        return response
