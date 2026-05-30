import asyncio

from discord import Interaction
from discord.app_commands import Choice, Group, command, describe, choices

from structlog import get_logger

from src.models import GameServer
from src.services.portainer import PortainerService
from src.settings.common import DISCORD_NOTIFICATIONS_CHANNEL_ID
from src.settings.nodes import MANAGER_NODE
from src.settings import games


SERVERS = [
    Choice(name=server.name, value=server)
    for server in games
    if isinstance(server, GameServer)
]


class ServersCommands(Group):

    def __init__(
        self,
        portainer: PortainerService,
    ):
        self.portainer = portainer
        self.logger = get_logger()
        super().__init__(
            name='servidor',
            description='Gerencie os servidores dedicados'
        )

    @command(name="ligar", description="Liga um servidor dedicado")
    @describe(game="Qual servidor?")
    @choices(game=SERVERS)
    async def turn_on(
        self,
        interaction: Interaction,
        game: Choice[GameServer],
    ):
        self.logger.info(
            f"Ligando o servidor...",
            user=interaction.user.name,
            game=game.value.name,
        )

        try:
            await interaction.response.defer(ephemeral=True)
            
            node_is_up = await self.portainer.node_is_up(
                endpoint_id=game.value.node.endpoint_id,
            )

            if not node_is_up:
                await interaction.edit_original_response(
                    content="⏳ Ligando a máquina remota..."
                )
                await self.portainer.start_container(
                    endpoint_id=MANAGER_NODE.endpoint_id,
                    container=game.value.node.controllers.turn_on,
                )
                await asyncio.sleep(5)  # Garantir que a máquina esteja ligando

            await interaction.edit_original_response(
                content=(
                    "⏳ Iniciando o servidor... "
                    "_(isso pode levar alguns minutos)_"
                )
            )
            self.logger.info(
                "Máquina ligada. Iniciando o servidor...",
                user=interaction.user.name,
                game=game.value.name,
            )
            await self.portainer.start_container(
                endpoint_id=game.value.node.endpoint_id,
                container=game.value.container_names[0],
            )
            await interaction.delete_original_response()
            await interaction.followup.send(
                content=(
                    "✅ Pronto! _Quando o servidor estiver pronto, "
                    f"avisarei em <#{DISCORD_NOTIFICATIONS_CHANNEL_ID}>._"
                ),
            )
        
        except ConnectionError:
            self.logger.info(
                "A máquina está demorando demais para ligar.",
                user=interaction.user.name,
                game=game.value.name,
            )
            await interaction.edit_original_response(
                content=(
                    "😢 A máquina está demorando mais que o esperado para ligar.\n"
                    "_Espere alguns segundos e tente rodar o comando novamente._"
                )
            )

        except Exception as e:
            self.logger.error(
                "Erro ao ligar o servidor!",
                user=interaction.user.name,
                game=game.value.name,
                error=str(e),
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._"
                )
            )

    @command(name="desligar", description="Desligar um servidor dedicado")
    @describe(game="Qual servidor?")
    @choices(game=SERVERS)
    async def turn_off(
        self,
        interaction: Interaction,
        game: Choice[GameServer],
    ):
        self.logger.info(
            "Desligando o servidor...",
            user=interaction.user.name,
            game=game.value.name,
        )

        try:
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_response(
                content="⏳ Desligando o servidor...",
            )
            await self.portainer.stop_container(
                endpoint_id=game.value.node.endpoint_id,
                container=game.value.container_names[0],
            )
            await asyncio.sleep(5)
            self.logger.info(
                "Servidor parado. Desligando a máquina...",
                user=interaction.user.name,
                game=game.value.name,
            )
            await interaction.edit_original_response(
                content="⏳ Desligando a máquina remota...",
            )
            await self.portainer.stop_container(
                endpoint_id=MANAGER_NODE.endpoint_id,
                container=game.value.node.controllers.turn_off,
            )
            await asyncio.sleep(5)
            await interaction.delete_original_response()
            await interaction.followup.send(
                content=(
                    "✅ Pronto! _Dentro de alguns segundos o "
                    "servidor estará completamente desligado e inacessível._"
                ),
            )
        except ConnectionError:
            self.logger.info(
                "Ignorando comando pois o servidor já está desligado.",
                user=interaction.user.name,
                game=game.value.name,
            )
            await interaction.edit_original_response(
                content="✅ O servidor já está desligado!",
            )

        except Exception as e:
            self.logger.error(
                "Erro ao desligar o servidor!",
                user=interaction.user.name,
                game=game.value.name,
                error=str(e),
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._"
                ),
            )
