from functools import cached_property

from pyportainer import Portainer
from pyportainer.models.portainer import Endpoint
from tenacity import AsyncRetrying, stop_after_attempt, wait_fixed

from src.settings.common import (
    PORTAINER_API_KEY,
    PORTAINER_API_URL,
)


class PortainerService:

    @cached_property
    def portainer(self) -> Portainer:
        return Portainer(
            api_url=PORTAINER_API_URL,
            api_key=PORTAINER_API_KEY
        )
    
    async def _get_endpoint(self, endpoint_id: int) -> Endpoint:
        endpoints = await self.portainer.get_endpoints()
        
        for endp in endpoints:
            if endp.id == endpoint_id:
                if endp.status != 1:
                    raise ConnectionError(f"Endpoint #{endpoint_id} está offline.")
                return endp
        
        raise ValueError(f"Endpoint #{endpoint_id} não encontrado.")
    
    async def node_is_up(self, endpoint_id: int) -> bool:
        try:
            await self._get_endpoint(endpoint_id)
            return True
        except ConnectionError:
            return False
    
    async def start_container(self, endpoint_id: int, container: str):
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(6),
            wait=wait_fixed(30),
            reraise=True
        ):
            with attempt:
                endpoint = await self._get_endpoint(endpoint_id)
                await self.portainer.start_container(
                    endpoint_id=endpoint.id,
                    container_id=container,
                )
    
    async def stop_container(self, endpoint_id: int, container: str):
        endpoint = await self._get_endpoint(endpoint_id)
        await self.portainer.stop_container(
            endpoint_id=endpoint.id,
            container_id=container,
        )
