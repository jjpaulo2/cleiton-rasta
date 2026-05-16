from pyportainer import Portainer
from pyportainer.exceptions import PortainerError

from settings import PORTAINER_ENDPOINT_ID, PORTAINER_CONTAINER_OCI


class TurnOnMachineService:

    def __init__(self, portainer: Portainer):
        self.portainer = portainer

    async def turn_on(self, machine_alias: str):
        containers = await self.portainer.get_containers(PORTAINER_ENDPOINT_ID)

        container = next(
            (c for c in containers if f"/{PORTAINER_CONTAINER_OCI}" in c.names),
            None,
        )
        if container is None:
            raise ValueError(f"Container '{PORTAINER_CONTAINER_OCI}' not found")

        exec_resp = await self.portainer._request(
            f"endpoints/{PORTAINER_ENDPOINT_ID}/docker/containers/{container.id}/exec",
            method="POST",
            json_body={
                "AttachStdout": True,
                "AttachStderr": True,
                "Cmd": ["turn-on-machine", machine_alias],
            },
        )
        exec_id = exec_resp["Id"]

        try:
            await self.portainer._request(
                f"endpoints/{PORTAINER_ENDPOINT_ID}/docker/exec/{exec_id}/start",
                method="POST",
                json_body={"Detach": True},
            )
        except PortainerError:
            # Docker exec/start may return a non-JSON or empty body when Detach=True
            pass
