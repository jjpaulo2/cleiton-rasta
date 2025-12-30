from discord import Interaction, Embed, Color
from discord.app_commands import Group, command

from src.notifications.minecraft import MinecraftNotifications
from src.settings import DISCORD_MINECRAFT_CHANNEL_ID
from src.integrations.oracle import OracleIntegration


class MinecraftCommands(Group):

    def __init__(
        self,
        oracle: OracleIntegration,
        notifications: MinecraftNotifications = MinecraftNotifications()
    ):
        self.oracle = oracle
        self.notifications = notifications
        super().__init__(
            name='minecraft',
            description='Gerencie o servidor de minecraft'
        )

    @command(name="ligar", description="Liga o servidor de Minecraft")
    async def turn_on(self, interaction: Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            await self.oracle.start_machine()
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    description="Comando enviado com sucesso!",
                    color=Color.green()
                )
            )
            await self.notifications.server_on(
                channel=interaction.client.get_channel(DISCORD_MINECRAFT_CHANNEL_ID), # type: ignore
                user=interaction.user
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
            await self.oracle.stop_machine()
            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    description="Comando enviado com sucesso!",
                    color=Color.green()
                )
            )
            await self.notifications.server_off(
                channel=interaction.client.get_channel(DISCORD_MINECRAFT_CHANNEL_ID), # type: ignore
                user=interaction.user
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

    @command(name="status", description="Verifica o status do servidor de Minecraft")
    async def status(self, interaction: Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            if not (await self.oracle.is_machine_running()):
                await interaction.followup.send(
                    ephemeral=True,
                    embed=Embed(
                        description="O servidor de Minecraft está desligado.",
                        color=Color.red()
                    )
                )
                return

            await interaction.followup.send(
                ephemeral=True,
                embed=Embed(
                    description="O servidor de Minecraft está ligado.",
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

    @command(name="custo", description="Exibe o custo do servidor de Minecraft para o mês atual")
    async def cost(self, interaction: Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            cost, currency, month = await self.oracle.get_current_cost()
            embed = Embed(
                description="Informações consultadas com sucesso!",
                color=Color.green()
            )
            embed.add_field(
                name='Mês',
                value=month,
                inline=False
            )
            embed.add_field(
                name='Valor',
                value=f"{currency} {cost:.2f}",
                inline=False
            )
            await interaction.followup.send(
                ephemeral=True,
                embed=embed
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
