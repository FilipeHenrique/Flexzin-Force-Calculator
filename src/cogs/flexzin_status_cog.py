import os
import discord
from discord import app_commands
from discord.ext import commands

from config import FLEXZIN_NICKNAME
from services.chess_com_api_client import ChessComApiClient
from services.flexzin_force_calculator import FlexzinForceCalculator
from utils.icons import icons


class FlexzinStatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.chess_com_api_client: ChessComApiClient = bot.chess_com_api_client
        self.flexzin_force_calculator: FlexzinForceCalculator = bot.flexzin_force_calculator

    @app_commands.command(
        name="flexzin_status",
        description="Verifica o status do jogador Flexzin"
    )
    async def flexzin_status(self, interaction: discord.Interaction):
        await interaction.response.defer()

        embed = discord.Embed(
            title="Flexzin Status",
            description="Status atuais do Flexzin",
            color=0xEDBE3E
        )

        player_profile = self.chess_com_api_client.get_player_profile_data(FLEXZIN_NICKNAME)
        avatar_url = player_profile.get("avatar")
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        flexzin_status = await self.chess_com_api_client.get_flexzin_status()

        def add_mode_section(mode_key: str, label: str):
            mode = flexzin_status.get(mode_key)
            if not mode:
                return

            rating = mode["last"]["rating"]
            best = mode["best"]["rating"]
            win = mode["record"]["win"]
            loss = mode["record"]["loss"]
            draw = mode["record"]["draw"]

            icon = icons[label]

            embed.add_field(
                name=f"{icon}",
                value=(
                    f"**Rating Atual:** {rating}\n"
                    f"**Melhor Rating:** {best}\n"
                    f"**Vitórias:** {win}\n"
                    f"**Derrotas:** {loss}\n"
                    f"**Empates:** {draw}\n"
                    f"━━━━━━━━━━━━"
                ),
                inline=False
            )

        add_mode_section("chess_rapid", "rapid")
        add_mode_section("chess_blitz", "blitz")
        add_mode_section("chess_bullet", "bullet")

        await interaction.followup.send(embed=embed)


async def setup(bot):
    await bot.add_cog(FlexzinStatusCog(bot))
