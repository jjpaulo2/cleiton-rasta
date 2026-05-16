from discord import Interaction, Embed, Color
from discord.app_commands import Group, command

from structlog import get_logger

from src.services.portainer import PortainerService
from src.settings import DISCORD_NOTIFICATIONS_CHANNEL_ID


class MinecraftCommands(Group):

    def __init__(
        self,
        portainer_service: PortainerService,
    ):
        self.portainer = portainer_service
        self.logger = get_logger()
        super().__init__(
            name='minecraft',
            description='Gerencie o servidor de Minecraft'
        )

    @command(name="ligar", description="Liga o servidor de Minecraft")
    async def turn_on(self, interaction: Interaction):
        self.logger.info(
            "Ligando o servidor de Minecraft...",
            user=interaction.user.name
        )

        try:
            await interaction.response.defer(ephemeral=True)
            await self.portainer.turn_on_heavy_node()
            await self.portainer.start_minecraft_server()
            await interaction.followup.send(
                ephemeral=True,
                content=(
                    "Comando enviado com sucesso!\n"
                    f"Quando o servidor estiver pronto, avisarei em <#{DISCORD_NOTIFICATIONS_CHANNEL_ID}>."
                )
            )

        except Exception as e:
            self.logger.error(
                "Erro ao ligar o servidor de Minecraft",
                user=interaction.user.name,
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

    @command(name="desligar", description="Desliga o servidor de Minecraft")
    async def turn_off(self, interaction: Interaction):
        self.logger.info(
            "Desligando o servidor de Minecraft...",
            user=interaction.user.name
        )

        try:
            await interaction.response.defer(ephemeral=True)
            await self.portainer.stop_minecraft_server()
            await self.portainer.turn_off_heavy_node()
            await interaction.followup.send(
                ephemeral=True,
                content=("Comando enviado com sucesso!")
            )
        
        except ConnectionError:
            self.logger.info(
                "Ignorando comando pois o servidor já está desligado.",
                user=interaction.user.name
            )
            await interaction.followup.send(
                ephemeral=True,
                content="O servidor já está desligado!"
            )

        except Exception as e:
            self.logger.error(
                "Erro ao desligar o servidor de Minecraft",
                user=interaction.user.name,
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
