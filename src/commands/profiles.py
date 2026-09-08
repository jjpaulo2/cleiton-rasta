from discord import Interaction, HTTPException
from discord.app_commands import Choice, Group, command, describe, choices, rename

from structlog import get_logger

from src.models import BotProfile
from src.services.profile import ProfileService
from src.settings import profiles


PROFILES = {
    profile.nickname: profile
    for profile in vars(profiles).values()
    if isinstance(profile, BotProfile)
}

PROFILES_CHOICES = [
    Choice(name=profile, value=profile)
    for profile in PROFILES.keys()
]


class ProfilesCommands(Group):

    def __init__(
        self,
        profile: ProfileService,
    ):
        self.profile = profile
        self.logger = get_logger()
        super().__init__(
            name='perfil',
            description='Customize o perfil do bot'
        )


    @command(name="alternar", description="Alterna uma configuração do perfil do bot")
    @rename(profile="perfil")
    @describe(profile="Selecione o perfil para o qual deseja alternar.")
    @choices(profile=PROFILES_CHOICES)
    async def switch(
        self,
        interaction: Interaction,
        profile: Choice[str],
    ):
        self.logger.info(
            f"Pedindo para alternar perfil...",
            user=interaction.user.name,
            profile=profile.value,
        )

        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_response(
                content=f"⏳ Alternando para o perfil ``{profile.value}``..."
            )
            await self.profile.set_full_profile(PROFILES[profile.value])
            await interaction.edit_original_response(
                content=f"✅ Perfil ``{profile.value}`` ativado com sucesso!"
            )
            
            self.logger.info(
                f"Perfil alternado com sucesso!",
                user=interaction.user.name,
                profile=profile.value
            )

        except HTTPException as exc:
            if 'too fast' in exc.text:
                await interaction.edit_original_response(
                    content="🔴 Você está alternando perfis rápido demais. Tente novamente em alguns segundos."
                )

            else:
                await interaction.edit_original_response(
                    content=(
                        "🔴 Ocorreu um erro na comunicação com o Discord. "
                        "_Tente novamente em alguns segundos ou peça ajuda a um dev._"
                    )
                )

            self.logger.error(
                f"HTTPException ao tentar alternar o perfil!",
                user=interaction.user.name,
                profile=profile.value,
                error=str(exc)
            )

        except Exception as exc:
            await interaction.edit_original_response(
                content="🔴 Ocorreu um erro ao tentar alternar o perfil."
            )
            self.logger.error(
                f"Erro ao tentar alternar o perfil!",
                user=interaction.user.name,
                profile=profile.value,
                error=str(exc)
            )
