from pathlib import Path

from discord import Client, ClientException, CustomActivity
from structlog import get_logger

from src.models import BotProfile
from src.settings import profiles
from src.settings.common import AVATARS_FOLDER


class ProfileService:

    def __init__(self, client: Client, guild_id: int):
        self.client = client
        self.guild_id = guild_id
        self.logger = get_logger()

    @property
    def guild(self):
        if my_guild := self.client.get_guild(self.guild_id):
            return my_guild
        raise ValueError(f"Guild with ID '{self.guild_id}' not found!")

    def _get_avatar_file(self, filename: str) -> Path:
            avatar = AVATARS_FOLDER / filename
            if not avatar.exists():
                raise FileNotFoundError(f"Avatar file '{filename}' not found in '{AVATARS_FOLDER}'.")
            return avatar

    async def _set_avatar(self, profile: BotProfile):
        try:
            if self.guild.me.nick == profile.nickname:
                return
            
            avatar = self._get_avatar_file(profile.avatar_filename)
            await self.guild.me.edit(avatar=avatar.read_bytes())
            self.logger.info("Avatar do bot alterado!", avatar=profile.avatar_filename)

        except ClientException as exc:
            self.logger.error(
                "Não foi possivel alterar o avatar do bot!",
                avatar=profile.avatar_filename,
                error=str(exc)
            )

    async def _set_presence(self, profile: BotProfile):
        try:
            await self.client.change_presence(
                activity=CustomActivity(
                    name=profile.presence,
                )
            )
            self.logger.info("Presença do bot alterada!", activity=profile.presence)

        except ClientException as exc:
            self.logger.error(
                "Não foi possivel alterar a atividade do bot!",
                activity=profile.presence,
                error=str(exc)
            )

    async def _set_username(self, profile: BotProfile):
        try:
            if self.guild.me.nick == profile.nickname:
                return

            await self.guild.me.edit(nick=profile.nickname)
            self.logger.info("Nome do bot alterado!", username=profile.nickname)

        except ClientException as exc:
            self.logger.error(
                "Não foi possivel alterar o nome do bot!",
                username=profile.nickname,
                error=str(exc)
            )

    async def _get_profile(self) -> BotProfile:
        for prof in vars(profiles).values():
            if isinstance(prof, BotProfile):
                if not self.guild.me.nick or self.guild.me.nick == prof.nickname:
                    return prof
        raise ValueError("No right BotProfile was found!")

    async def set_default_presence(self):
        profile = await self._get_profile()
        await self._set_presence(profile)

    async def set_full_profile(self, profile: BotProfile):
        await self._set_avatar(profile)
        await self._set_presence(profile)
        await self._set_username(profile)
