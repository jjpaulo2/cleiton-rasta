from asyncio import sleep

from pyportainer import Portainer
from tenacity import retry, stop_after_attempt, wait_fixed

from src.settings import (
    MINECRAFT_CONTAINER_NAME,
    ORACLE_CLI_IMAGE,
    PORTAINER_MANAGER_NODE_ENDPOINT_ID,
    PORTAINER_HEAVY_NODE_ENDPOINT_ID,
    CLUSTER_HEAVY_NODE_ID
)


class PortainerService:

    def __init__(self, portainer: Portainer):
        self.portainer = portainer

    async def _get_container_id(self, container_name: str, endpoint_id: int) -> str | None:
        endpoints = await self.portainer.get_endpoints()
        
        for endp in endpoints:
            if endp.id == endpoint_id:
                if endp.status != 1:
                    raise ConnectionError(f"Endpoint #{endpoint_id} está offline.")
                break
        else:
            raise ValueError(f"Endpoint #{endpoint_id} não encontrado.")

        for container in await self.portainer.get_containers(endpoint_id):
            if f"/{container_name}" in container.names:
                return container.id
            
        return None
    
    async def _run_container(self, container_name: str, endpoint_id: int, image: str, command: list[str]):
        container_id = await self._get_container_id(container_name, endpoint_id)
        
        if not container_id:
            container = await self.portainer.container_create(
                endpoint_id=endpoint_id,
                name=container_name,
                image=image,
                config={
                    "Entrypoint": command,
                }
            )
            container_id = container.id

        await self.portainer.start_container(
            endpoint_id=endpoint_id,
            container_id=container_id
        )

    async def turn_off_heavy_node(self):
        await self._run_container(
            container_name="turn-off-cluster-heavy-node-0",
            endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            image=ORACLE_CLI_IMAGE,
            command=[
                "oci",
                "compute",
                "instance",
                "action",
                "--instance-id",
                CLUSTER_HEAVY_NODE_ID,
                "--action",
                "SOFTSTOP",
                "--auth",
                "instance_principal"
            ]
        )

    async def turn_on_heavy_node(self):
        await self._run_container(
            container_name="turn-on-cluster-heavy-node-0",
            endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            image=ORACLE_CLI_IMAGE,
            command=[
                "oci",
                "compute",
                "instance",
                "action",
                "--instance-id",
                CLUSTER_HEAVY_NODE_ID,
                "--action",
                "START",
                "--auth",
                "instance_principal"
            ]
        )
    
    @retry(
        stop=stop_after_attempt(6),
        wait=wait_fixed(10)
    )
    async def start_minecraft_server(self):
        await self.portainer.start_container(
            endpoint_id=PORTAINER_HEAVY_NODE_ENDPOINT_ID,
            container_id=await self._get_container_id(
                container_name=MINECRAFT_CONTAINER_NAME,
                endpoint_id=PORTAINER_HEAVY_NODE_ENDPOINT_ID,
            ),
        )

    async def stop_minecraft_server(self):
        await self.portainer.stop_container(
            endpoint_id=PORTAINER_HEAVY_NODE_ENDPOINT_ID,
            container_id=await self._get_container_id(
                container_name=MINECRAFT_CONTAINER_NAME,
                endpoint_id=PORTAINER_HEAVY_NODE_ENDPOINT_ID,
            )
        )
