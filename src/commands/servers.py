import asyncio

from discord import Interaction
from discord.app_commands import Choice, Group, command, describe, choices, rename

from structlog import get_logger

from src.models import GameServer
from src.services.portainer import PortainerService
from src.settings.common import DISCORD_NOTIFICATIONS_CHANNEL_ID
from src.settings.nodes import MANAGER_NODE
from src.settings import games


SERVERS = {
    server.name: server
    for server in vars(games).values()
    if isinstance(server, GameServer)
}

SERVERS_CHOICES = [
    Choice(name=server, value=server)
    for server in SERVERS.keys()
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


    @command(name="ligar", description="Liga um servidor dedicado de jogo")
    @rename(game="jogo")
    @describe(game="Selecione o servidor que deseja ligar.")
    @choices(game=SERVERS_CHOICES)
    async def turn_on(
        self,
        interaction: Interaction,
        game: Choice[str],
    ):
        self.logger.info(
            f"Ligando o servidor...",
            user=interaction.user.name,
            game=game.value,
        )

        try:
            await interaction.response.defer(ephemeral=True)
            
            game_server = SERVERS[game.value]
            node_is_up = await self.portainer.node_is_up(
                endpoint_id=game_server.node.endpoint_id,
            )

            if not node_is_up:
                await interaction.edit_original_response(
                    content="⏳ Ligando a máquina remota..."
                )
                await self.portainer.start_container(
                    endpoint_id=MANAGER_NODE.endpoint_id,
                    container=game_server.node.controllers.turn_on,
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
                game=game.value,
            )
            
            for container_name in game_server.container_names:
                await self.portainer.start_container(
                    endpoint_id=game_server.node.endpoint_id,
                    container=container_name,
                )
            
            await interaction.edit_original_response(
                content=(
                    f"✅ Pronto! _Quando o servidor de **{game.value}** estiver "
                    f"pronto, avisarei em <#{DISCORD_NOTIFICATIONS_CHANNEL_ID}>._"
                ),
            )
        
        except ConnectionError:
            self.logger.info(
                "A máquina está demorando demais para ligar.",
                user=interaction.user.name,
                game=game.value,
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
                game=game.value,
                error=str(e),
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._"
                )
            )


    @command(name="desligar", description="Desligar um servidor dedicado de jogo")
    @rename(
        game="jogo",
        turn_off_machine="desligar_máquina"
    )
    @describe(
        game="Selecione o servidor que deseja desligar.",
        turn_off_machine="Deixe sempre essa opção ativa para garantir economia de recursos."
    )
    @choices(game=SERVERS_CHOICES)
    async def turn_off(
        self,
        interaction: Interaction,
        game: Choice[str],
        turn_off_machine: bool = True,
    ):
        self.logger.info(
            "Desligando o servidor...",
            user=interaction.user.name,
            game=game.value,
        )

        try:
            game_server = SERVERS[game.value]
            await interaction.response.defer(ephemeral=True)
            await interaction.edit_original_response(
                content="⏳ Desligando o servidor...",
            )
            
            for container_name in game_server.container_names[::-1]:
                await self.portainer.stop_container(
                    endpoint_id=game_server.node.endpoint_id,
                    container=container_name,
                )

            await asyncio.sleep(5)

            if turn_off_machine:
                self.logger.info(
                    "Servidor parado. Desligando a máquina...",
                    user=interaction.user.name,
                    game=game.value,
                )
                await interaction.edit_original_response(
                    content="⏳ Desligando a máquina remota...",
                )
                await self.portainer.stop_container(
                    endpoint_id=MANAGER_NODE.endpoint_id,
                    container=game_server.node.controllers.turn_off,
                )
                await asyncio.sleep(5)
            
            await interaction.edit_original_response(
                content=(
                    "✅ Pronto! _Dentro de alguns segundos o servidor de "
                    f"**{game.value}** estará completamente desligado e inacessível._"
                ),
            )
        except ConnectionError:
            self.logger.info(
                "Ignorando comando pois o servidor já está desligado.",
                user=interaction.user.name,
                game=game.value,
            )
            await interaction.edit_original_response(
                content="✅ O servidor já está desligado!",
            )

        except Exception as e:
            self.logger.error(
                "Erro ao desligar o servidor!",
                user=interaction.user.name,
                game=game.value,
                error=str(e),
            )
            await interaction.edit_original_response(
                content=(
                    "🔴 Ocorreu um erro ao tentar executar o comando!\n"
                    "_Se você for leigo, não se desespere. Chame um dev para resolver isso._"
                ),
            )
