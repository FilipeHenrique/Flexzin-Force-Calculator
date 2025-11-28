import asyncio
import os
import discord
from discord import Embed
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
from services.flexzin_force_calculator import FlexzinForceCalculator
from services.chess_com_api_client import ChessComApiClient
from infrastructure.redis_repository import RedisRepository
import logging

load_dotenv()

FLEXZIN_NICKNAME = os.getenv("FLEXZIN_NICKNAME", "")
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")

# --- Serviços ---
chess_com_api_client = ChessComApiClient()
redis_repository = RedisRepository()
flexzin_force_calculator = FlexzinForceCalculator(chess_com_api_client, redis_repository)

# --- Bot ---
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

icons = {
    "rapid": "<:rapid:1442245397589528741> Rapid",
    "blitz": "<:blitz:1442245840482861259> Blitz",
    "bullet": "<:bullet:1442246135988228217> Bullet",
}

# ----------------------------------------
# EVENTOS E COMANDOS (usam o bot global)
# ----------------------------------------

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Bot pronto! Logado como {bot.user}")

@bot.tree.command(name="flexzin_force", description="Verifica a força do jogador em relação ao Flexzin")
@app_commands.describe(player_nickname="Nickname do jogador no Chess.com")
async def flexzin_force(interaction: discord.Interaction, player_nickname: str):

    player_nickname = player_nickname.strip().replace(" ", "_")
    player_games_found = False

    embed = Embed(
        title=f"<:chesscom_logo:1442243838432252116> {player_nickname}",
        url=f"https://www.chess.com/member/{(player_nickname)}",
        description="Resultado dos cálculos de Flexzin Force ",
        color=0xEDBE3E
    )

    await interaction.response.defer()

    player_profile = chess_com_api_client.get_player_profile_data(player_nickname)
    if not player_profile:
        embed.description = f"O jogador {player_nickname} não existe no Chess.com"
        await interaction.followup.send(embed=embed)
        return

    try:
        result = await asyncio.wait_for(
            flexzin_force_calculator.get_flexzin_force_by_time_control(player_nickname),
            timeout=30
        )
    except Exception as e:
        await interaction.followup.send(f"❌ Ocorreu um erro inesperado: {e}")
        logging.exception("Erro inesperado durante flexzin_force")  
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
            embed.add_field(name=f"{label}", value=f"{value} — igualdade", inline=False)
        else:
            embed.add_field(name=f"{label}", value=f"{value} — {percent}% de {status}", inline=False)

    if not player_games_found:
        embed.description = f"O jogador {player_nickname} não tem partidas rated nos últimos 6 meses para comparar com o Flexzin."
    
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="flexzin_status", description="Comando para verificar o status do jogador Flexzin", guild=discord.Object(id=1076903242681815170))
async def flexzin_status(interaction: discord.Interaction):
    await interaction.response.defer()

    embed = Embed(
        title="Flexzin Status",
        description="Status atuais do Flexzin",
        color=0xEDBE3E
    )

    player_profile = chess_com_api_client.get_player_profile_data(FLEXZIN_NICKNAME)
    avatar_url = player_profile.get("avatar")
    if avatar_url:
        embed.set_thumbnail(url=avatar_url)

    flexzin_status = await chess_com_api_client.get_flexzin_status()

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


# ----------------------------------------
# MAIN (roda o bot global)
# ----------------------------------------
async def main():
    await chess_com_api_client.init()

    try:
        await bot.start(DISCORD_TOKEN)

    finally:
        await redis_repository.close()
        await chess_com_api_client.close_session()


if __name__ == "__main__":
    asyncio.run(main())