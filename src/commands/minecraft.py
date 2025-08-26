from discord import Interaction, Embed, Color
from discord.app_commands.checks import has_role
from discord.app_commands import (
    Group,
    command,
    check,
    CheckFailure,
    AppCommandError,
    describe
)

from src.integrations.rcon import RconIntegration
from src.settings import DISCORD_ADMIN_ROLE_ID, DISCORD_MINECRAFT_CHANNEL_ID
from src.integrations.oracle import OracleIntegration
from src.utils.discord import is_channel


class MinecraftCommands(Group):

    def __init__(self, oracle: OracleIntegration, rcon: RconIntegration) -> None:
        self.oracle = oracle
        self.rcon = rcon
        super().__init__(
            name='minecraft',
            description='Gerencie o servidor de minecraft'
        )

    @command(name="ligar", description="Liga o servidor de Minecraft")
    async def turn_on(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            await self.oracle.start_machine()
            await interaction.followup.send("Comando enviado com sucesso!")

        except Exception as e:
            await interaction.followup.send(
                "Ocorreu um erro ao tentar ligar o servidor de Minecraft!",
                embed=Embed(
                    description=str(e),
                    color=Color.red()
                )
            )

    @command(name="desligar", description="Desliga o servidor de Minecraft")
    async def turn_off(self, interaction: Interaction):
        try:
            await interaction.response.defer()
            await self.oracle.stop_machine()
            await interaction.followup.send("Comando enviado com sucesso!")

        except Exception as e:
            await interaction.followup.send(
                "Ocorreu um erro ao tentar desligar o servidor de Minecraft!",
                embed=Embed(
                    description=str(e),
                    color=Color.red()
                )
            )

    @command(name="comando", description="Envia comando ao servidor de Minecraft")
    @describe(command="O comando que será enviado ao servidor")
    @has_role(DISCORD_ADMIN_ROLE_ID)
    @check(is_channel(DISCORD_MINECRAFT_CHANNEL_ID))
    async def send_command(self, interaction: Interaction, command: str):
        try:
            await interaction.response.defer()
            response = await self.rcon.send_command(command)
            embed = Embed(color=Color.green())
            embed.set_author(
                name=interaction.user.display_name,
                icon_url=interaction.user.display_avatar.url
            )
            embed.add_field(
                name="Comando",
                value=command,
                inline=False
            )
            embed.add_field(
                name="Saída",
                value=response[:1024],
                inline=False
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                "Ocorreu um erro ao tentar enviar o comando ao servidor de Minecraft!",
                embed=Embed(
                    description=str(e),
                    color=Color.red()
                )
            )

    @send_command.error
    async def _send_command_error(self, interaction: Interaction, error: AppCommandError):
        if isinstance(error, CheckFailure):
            await interaction.response.send_message(
                f"Por motivos de segurança, este comando só pode ser enviado no canal <#{DISCORD_MINECRAFT_CHANNEL_ID}>.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Ocorreu um erro ao processar o comando.",
                ephemeral=True
            )
