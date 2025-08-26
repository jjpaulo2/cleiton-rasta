from discord import Interaction, Embed, Color
from discord.app_commands import Group, command

from src.integrations.minedoscrazy import MineDosCrazy


class MinecraftCommands(Group):

    def __init__(self, integration: MineDosCrazy) -> None:
        self.integration = integration
        super().__init__(
            name='minecraft',
            description='Gerencie o servidor de minecraft'
        )

    @command(name="ligar", description="Liga o servidor de Minecraft")
    async def turn_on(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            await self.integration.start_machine()
            await interaction.followup.send("Comando enviado com sucesso!")

        except Exception as e:
            await interaction.followup.send(
                "Ocorreu um erro ao tentar desligar o servidor de Minecraft!",
                embed=Embed(
                    description=str(e),
                    color=Color.red()
                )
            )

    @command(name="desligar", description="Desliga o servidor de Minecraft")
    async def turn_off(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            await self.integration.stop_machine()
            await interaction.followup.send("Comando enviado com sucesso!")

        except Exception as e:
            await interaction.followup.send(
                "Ocorreu um erro ao tentar desligar o servidor de Minecraft!",
                embed=Embed(
                    description=str(e),
                    color=Color.red()
                )
            )
