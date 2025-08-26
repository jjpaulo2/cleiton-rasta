import asyncio

from mcrcon import MCRcon


class RconIntegration:

    def __init__(self, host: str, password: str, port: int) -> None:
        self.host = host
        self.password = password
        self.port = port

    async def send_command(self, command: str) -> str:
        with MCRcon(self.host, self.password, self.port) as client:
            return await asyncio.to_thread(client.command, command)
