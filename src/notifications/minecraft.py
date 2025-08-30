from discord import Embed, User, Member, Color, TextChannel

from src.settings import MINECRAFT_DOMAIN_NAME


class MinecraftNotifications:

    async def server_on(self, channel: TextChannel, user: User | Member):
        embed = Embed(
            title="Servidor ligado!",
            description="Dentro de alguns segundos tudo estará disponível.",
            color=Color.green()
        )
        embed.add_field(
            name='Endereço / IP',
            value=f"`{MINECRAFT_DOMAIN_NAME}`"
        )
        embed.add_field(
            name='Mapa online',
            value=f"[map.{MINECRAFT_DOMAIN_NAME}](https://map.{MINECRAFT_DOMAIN_NAME})"
        )
        embed.add_field(
            name='Monitoramento',
            value=f"[monitoring.{MINECRAFT_DOMAIN_NAME}](https://monitoring.{MINECRAFT_DOMAIN_NAME})"
        )
        embed.set_author(
            name=user.display_name,
            icon_url=user.avatar.url if user.avatar else None
        )
        await channel.send(embed=embed)

    async def server_off(self, channel: TextChannel, user: User | Member):
        embed = Embed(
            title="Servidor desligado!",
            description="Agora não é mais possível se conectar ao servidor.",
            color=Color.red()
        )
        embed.set_author(
            name=user.display_name,
            icon_url=user.avatar.url if user.avatar else None
        )
        await channel.send(embed=embed)