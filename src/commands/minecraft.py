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
            await interaction.edit_original_response(
                content="⏳ Ligando a máquina remota..."
            )
            await self.portainer.turn_on_heavy_node()
            await interaction.edit_original_response(
                content=(
                    "✅ Máquina ligada com sucesso!\n\n"
                    "⏳ Iniciando o servidor de Minecraft... _(isso pode levar alguns minutos)_"
                )
            )
            self.logger.info(
                "Máquina ligada. Iniciando o servidor de Minecraft...",
                user=interaction.user.name
            )
            await self.portainer.start_minecraft_server()
            await interaction.edit_original_response(
                content=(
                    "✅ Máquina ligada com sucesso!\n\n"
                    "✅ Servidor de Minecraft iniciado com sucesso!\n\n"
                    f"_Quando o servidor estiver pronto, avisarei em <#{DISCORD_NOTIFICATIONS_CHANNEL_ID}>._"
                )
            )

        except Exception as e:
            self.logger.error(
                "Erro ao ligar o servidor de Minecraft",
                user=interaction.user.name,
                error=str(e)
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._\n\n"
                    f"```{str(e)}```"
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
            await interaction.edit_original_response(
                content="⏳ Desligando o servidor de Minecraft..."
            )
            await self.portainer.stop_minecraft_server()
            self.logger.info(
                "Servidor parado. Desligando a máquina...",
                user=interaction.user.name
            )
            await interaction.edit_original_response(
                content=(
                    "✅ Servidor desligado com sucesso!\n\n"
                    "⏳ Desligando a máquina remota..."
                )
            )
            await self.portainer.turn_off_heavy_node()
            await interaction.edit_original_response(
                content=(
                    "✅ Servidor desligado com sucesso!\n\n"
                    "✅ Máquina desligada com sucesso!\n\n"
                    f"_Dentro de alguns segundos o servidor estará completamente desligado e inacessível._"
                )
            )
        
        except ConnectionError:
            self.logger.info(
                "Ignorando comando pois o servidor já está desligado.",
                user=interaction.user.name
            )
            await interaction.edit_original_response(
                content="✅ O servidor já está desligado!"
            )

        except Exception as e:
            self.logger.error(
                "Erro ao desligar o servidor de Minecraft",
                user=interaction.user.name,
                error=str(e)
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._\n\n"
                    f"```{str(e)}```"
                )
            )
