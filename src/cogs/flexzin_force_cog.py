import asyncio
import discord
from discord import app_commands
from discord.ext import commands

from bot import FlexzinForceBot

from utils.icons import icons
from utils.logger import logger

class FlexzinForceCog(commands.Cog):
    def __init__(self, bot: FlexzinForceBot):
        self.bot = bot
        self.chess_com_api_client = bot.chess_com_api_client
        self.flexzin_force_calculator = bot.flexzin_force_calculator

    @app_commands.command(
        name="flexzin_force",
        description="Compara a força do jogador em relação ao Flexzin"
    )
    @app_commands.describe(player_nickname="Nickname do jogador no Chess.com")
    async def flexzin_force(self, interaction: discord.Interaction, player_nickname: str):
        player_nickname = player_nickname.strip().replace(" ", "_")
        player_games_found = False

        embed = discord.Embed(
            title=f"<:chesscom_logo:1442243838432252116> {player_nickname}",
            url=f"https://www.chess.com/member/{player_nickname}",
            description="Resultado dos cálculos de Flexzin Force",
            color=0xEDBE3E
        )

        await interaction.response.defer()

        player_profile = self.chess_com_api_client.get_player_profile_data(player_nickname)
        if not player_profile:
            embed.description = f"O jogador **{player_nickname}** não existe no Chess.com."
            await interaction.followup.send(embed=embed)
            return

        try:
            result = await asyncio.wait_for(
                self.flexzin_force_calculator.get_flexzin_force_by_time_control(player_nickname),
                timeout=30
            )
        except Exception as e:
            await interaction.followup.send(f"❌ Erro inesperado: {e}")
            logger.exception("Erro inesperado durante flexzin_force")
            return

        avatar_url = player_profile.get("avatar")
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        for time_control, label in icons.items():
            value = result.get(time_control)
            if not value:
                continue
            
            player_games_found = True

            if value > 1.0:
                status = "superioridade"
                percent = abs(int((value - 1.0) * 100))
            elif value < 1.0:
                status = "inferioridade"
                percent = abs(int((value - 1.0) * 100))
            else:
                status = "igualdade"
                percent = 0

            if status == "igualdade":
                field_value = f"{value:.2f} — igualdade"
            else:
                field_value = f"{value:.2f} — **{percent}%** de {status}"

            embed.add_field(name=f"{label}", value=field_value, inline=False)

        if not player_games_found:
            embed.description = (
                f"O jogador **{player_nickname}** não tem partidas rated nos últimos 6 meses "
                "para comparar com o Flexzin."
            )

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FlexzinForceCog(bot))
