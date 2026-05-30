from dataclasses import dataclass


@dataclass
class HeavyNodeControllerContainers:
    turn_on: str
    turn_off: str

@dataclass
class HeavyNode:
    name: str
    endpoint_id: int
    controllers: HeavyNodeControllerContainers

@dataclass
class Node:
    name: str
    endpoint_id: int

@dataclass
class GameServer:
    name: str
    container_names: list[str]
    node: HeavyNode
