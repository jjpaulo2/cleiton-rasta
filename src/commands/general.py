from discord import Interaction, Embed, Color, TextChannel, VoiceChannel
from discord.app_commands import Group, command
from structlog import get_logger

from src.views.confirmation import ConfirmationView


class GeneralCommands(Group):

    def __init__(self):
        self.logger = get_logger()
        super().__init__(
            name='geral',
            description='Comandos gerais de ajuda e administração'
        )

    @command(name="limpar_canal", description="Apaga todas as mensagens do canal atual")
    async def clean_channel(self, interaction: Interaction):
        self.logger.info(
            "Tentando limpar o canal...",
            user=interaction.user.name,
            channel=interaction.channel.name
        )

        try:
            if not isinstance(interaction.channel, (TextChannel, VoiceChannel)):
                await interaction.response.send_message(
                    "Este comando não pode ser usado neste tipo de canal.",
                    ephemeral=True
                )
                return

            confirmation = ConfirmationView()
            await interaction.response.send_message(
                ephemeral=True,
                view=confirmation,
                embed=Embed(
                    description="Tem certeza que deseja limpar este canal? Esta ação é irreversível!",
                    color=Color.yellow()
                ),
            )
            await confirmation.wait()

            if confirmation.is_confirmed:
                self.logger.info(
                    "Ação de limpar canal confirmada! Limpando canal...",
                    user=interaction.user.name,
                    channel=interaction.channel.name
                )
                await interaction.channel.purge(
                    limit=None,
                    bulk=False
                )
                self.logger.info(
                    "Canal limpo com sucesso!",
                    user=interaction.user.name,
                    channel=interaction.channel.name
                )
                await interaction.response.edit_message(
                    embed=Embed(
                        description="Canal limpo com sucesso!",
                        color=Color.green()
                    )
                )

        except Exception as e:
            self.logger.error(
                "Erro ao tentar limpar o canal",
                user=interaction.user.name,
                channel=interaction.channel.name,
                error=str(e)
            )
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    title="Ocorreu um erro ao tentar executar o comando!",
                    description=str(e),
                    color=Color.red()
                )
            )
