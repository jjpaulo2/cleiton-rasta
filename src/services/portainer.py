from pyportainer import Portainer
from pyportainer.models.portainer import Endpoint
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
    
    async def _get_endpoint(self, endpoint_id: int) -> Endpoint:
        endpoints = await self.portainer.get_endpoints()
        
        for endp in endpoints:
            if endp.id == endpoint_id:
                if endp.status != 1:
                    raise ConnectionError(f"Endpoint #{endpoint_id} está offline.")
                return endp
        
        raise ValueError(f"Endpoint #{endpoint_id} não encontrado.")

    async def heavy_node_is_up(self) -> bool:
        try:
            await self._get_endpoint(PORTAINER_HEAVY_NODE_ENDPOINT_ID)
            return True
        except ConnectionError:
            return False

    async def turn_off_heavy_node(self):
        endpoint = await self._get_endpoint(PORTAINER_MANAGER_NODE_ENDPOINT_ID)
        await self.portainer.start_container(
            endpoint_id=endpoint.id,
            container_id=TURN_OFF_HEAVY_NODE_CONTAINER_NAME,
        )

    async def turn_on_heavy_node(self):
        endpoint = await self._get_endpoint(PORTAINER_MANAGER_NODE_ENDPOINT_ID)
        await self.portainer.start_container(
            endpoint_id=endpoint.id,
            container_id=TURN_ON_HEAVY_NODE_CONTAINER_NAME,
        )

    async def start_minecraft_server(self):
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_fixed(30),
            reraise=True
        ):
            with attempt:
                endpoint = await self._get_endpoint(PORTAINER_HEAVY_NODE_ENDPOINT_ID)
                await self.portainer.start_container(
                    endpoint_id=endpoint.id,
                    container_id=MINECRAFT_CONTAINER_NAME,
                )

    async def stop_minecraft_server(self):
        endpoint = await self._get_endpoint(PORTAINER_HEAVY_NODE_ENDPOINT_ID)
        await self.portainer.stop_container(
            endpoint_id=endpoint.id,
            container_id=MINECRAFT_CONTAINER_NAME,
        )
