from src.models import HeavyNode, HeavyNodeControllerContainers


MANAGER_NODE = HeavyNode(
    name='cluster-node-0',
    endpoint_id=14,
)

HEAVY_NODE = HeavyNode(
    name='cluster-heavy-node-0',
    endpoint_id=16,
    controllers=HeavyNodeControllerContainers(
        turn_on='turn-on-cluster-node-heavy-0',
        turn_off='turn-off-cluster-node-heavy-0',
    ),
)
