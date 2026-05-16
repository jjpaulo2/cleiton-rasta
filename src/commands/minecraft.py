from discord import Interaction, Embed, Color
from discord.app_commands import Group, command

from src.services.send_command import SendCommandService
from src.settings import PORTAINER_NODE_GAMES


class MinecraftCommands(Group):

    def __init__(
        self,
        command_service: SendCommandService,
    ):
        self.command_service = command_service
        super().__init__(
            name='minecraft',
            description='Gerencie o servidor de minecraft'
        )

    @command(name="ligar", description="Liga o servidor de Minecraft")
    async def turn_on(self, interaction: Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await self.command_service.turn_on(PORTAINER_NODE_GAMES)
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    description="Comando enviado com sucesso!",
                    color=Color.green()
                )
            )

        except Exception as e:
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
        try:
            await interaction.response.defer(ephemeral=True)
            await self.command_service.turn_off(PORTAINER_NODE_GAMES)
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    description="Comando enviado com sucesso!",
                    color=Color.green()
                )
            )

        except Exception as e:
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    title="Ocorreu um erro ao tentar executar o comando!",
                    description=str(e),
                    color=Color.red()
                )
            )
