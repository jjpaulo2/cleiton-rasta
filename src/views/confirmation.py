from discord import ButtonStyle, Color, Embed, Interaction
from discord.ui import View, Button, button


class ConfirmationView(View):

    def __init__(self, *, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.is_confirmed = False

    @button(label="Confirmar", style=ButtonStyle.success)
    async def confirm(self, interaction: Interaction, button: Button):
        self.is_confirmed = True
        self.stop()
        await interaction.response.edit_message(
            embed=Embed(
                description="Executando ação, por favor aguarde...",
                color=Color.yellow()
            ),
            view=None,
        )

    @button(label="Cancelar", style=ButtonStyle.danger)
    async def cancel(self, interaction: Interaction, button: Button):
        self.stop()
        await interaction.response.edit_message(
            embed=Embed(
                description="Ação cancelada!",
                color=Color.green()
            ),
            view=None,
        )
