from pyportainer import Portainer
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

from src.settings import (
    MINECRAFT_CONTAINER_NAME,
    PORTAINER_MANAGER_NODE_ENDPOINT_ID,
    PORTAINER_HEAVY_NODE_ENDPOINT_ID,
    TURN_OFF_HEAVY_NODE_CONTAINER_NAME,
    TURN_ON_HEAVY_NODE_CONTAINER_NAME
)


class PortainerService:

    def __init__(self, portainer: Portainer):
        self.portainer = portainer

    async def _get_container_id(self, container_name: str, endpoint_id: int) -> str:
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
            
        raise ValueError(f"Container '{container_name}' não encontrado no endpoint #{endpoint_id}.")

    async def turn_off_heavy_node(self):
        await self.portainer.start_container(
            endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            container_id=await self._get_container_id(
                container_name=TURN_OFF_HEAVY_NODE_CONTAINER_NAME,
                endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            ),
        )

    async def turn_on_heavy_node(self):
        await self.portainer.start_container(
            endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            container_id=await self._get_container_id(
                container_name=TURN_ON_HEAVY_NODE_CONTAINER_NAME,
                endpoint_id=PORTAINER_MANAGER_NODE_ENDPOINT_ID,
            ),
        )

    async def start_minecraft_server(self):
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_fixed(15)
        ):
            with attempt:
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
