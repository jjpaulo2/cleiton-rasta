from abc import ABC

from pyportainer import Portainer

from src.settings import PORTAINER_CONTAINER_OCI, PORTAINER_ENDPOINT_ID


class SendCommandService:

    def __init__(self, portainer: Portainer):
        self.portainer = portainer

    async def _get_container_id(self, container_name: str) -> str:
        containers = await self.portainer.get_containers(PORTAINER_ENDPOINT_ID)
        for c in containers:
            if f"/{container_name}" in c.names:
                return c.id
        raise ValueError(f"Container '{container_name}' not found")
    
    async def _send_exec_command(self, container_id: str, cmd: list[str]):
        exec_resp = await self.portainer._request(
            f"endpoints/{PORTAINER_ENDPOINT_ID}/docker/containers/{container_id}/exec",
            method="POST",
            json_body={
                "AttachStdout": True,
                "AttachStderr": True,
                "Cmd": cmd,
            },
        )
        return exec_resp["Id"]
    
    async def _send_start_command(self, exec_id: str):
        await self.portainer._request(
            f"endpoints/{PORTAINER_ENDPOINT_ID}/docker/exec/{exec_id}/start",
            method="POST",
            json_body={"Detach": True},
        )

    async def turn_off(self, machine_alias: str):
        container_id = await self._get_container_id(PORTAINER_CONTAINER_OCI)
        
        exec_id = await self._send_exec_command(
            container_id=container_id,
            cmd=[
                "turn-off-machine",
                machine_alias
            ]
        )

        await self._send_start_command(exec_id)

    async def turn_on(self, machine_alias: str):
        container_id = await self._get_container_id(PORTAINER_CONTAINER_OCI)

        exec_id = await self._send_exec_command(
            container_id=container_id,
            cmd=[
                "turn-on-machine",
                machine_alias
            ]
        )

        await self._send_start_command(exec_id)