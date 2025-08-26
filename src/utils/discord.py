from discord import Interaction


def is_channel(channel_id: int):
    async def predicate(interaction: Interaction) -> bool:
        return interaction.channel_id == channel_id
    return predicate
