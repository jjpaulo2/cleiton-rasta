from pyportainer import Portainer

from settings import PORTAINER_ENDPOINT_ID


class TurnOnMachineService:

    def __init__(self, portainer: Portainer):
        self.portainer = portainer
    
    async def turn_on(self, machine_alias: str):
        containers = await self.portainer.get_containers(PORTAINER_ENDPOINT_ID)
