from discord import Client, CustomActivity


async def set_default_activity(client: Client):
    await client.change_presence(
        activity=CustomActivity(name="Xingando caixistas na internet")
    )
