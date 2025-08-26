import asyncio

from oci import config
from oci.core import ComputeClient


class OracleIntegration:

    def __init__(self, machine_id: str) -> None:
        self.config = config.from_file()
        self.client = ComputeClient(self.config)
        self.machine_id = machine_id

    async def start_machine(self):
        await asyncio.to_thread(self.client.instance_action, self.machine_id, "START")

    async def stop_machine(self):
        await asyncio.to_thread(self.client.instance_action, self.machine_id, "SOFTSTOP")
