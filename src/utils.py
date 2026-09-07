from discord import Client, CustomActivity, Member, ClientException
from structlog import get_logger


logger = get_logger()


async def set_default_activity(client: Client):
    await client.change_presence(
        activity=CustomActivity(name="🤬 Xingando caixistas na internet")
    )


async def set_nickname(member: Member, nickname: str | None = None):
    try:
        if member.nick == nickname:
            return

        await member.edit(nick=nickname)
        logger.info("Apelido alterado!", member=member.name, nickname=nickname)

    except ClientException as exc:
        logger.error(
            "Não foi possivel alterar o apelido!",
            member=member.name,
            nickname=nickname,
            error=str(exc)
        )
