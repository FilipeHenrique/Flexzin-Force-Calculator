from math import sqrt
import requests
from datetime import datetime
import asyncio

# TO DO
    # QUEBRAR CÓDIGO EM CLASSES ESPECÍFICAS
    # CODAR PARALELIMSMO PARA MELHORAR PERFORMANCE

CHESS_COM_BASE_URL = "https://api.chess.com"
FLEXZIN_NICKNAME = "FIexPrime"
TIME_CONTROLS = ["rapid", "blitz", "bullet"]
Z = 1.96


# TO DO, FAZER SER DE FATO ASYNC, REQUESTS BLOQUEIA A THREAD
async def get_games_from_chess_com(player_nickname, current_year, current_month):
    # header to avoid cloudflare blocking
    headers = {"User-Agent": "flexzin-force/1.0"}
    response = requests.get(f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}/games/{current_year}/{current_month}", headers=headers)
    return response

# TO DO, ARMAZENAR EM TASKS PRA FAZER ASYNC AO INVÉS DE CHAMAR EM O(N)
async def get_player_games_from_last_twelve_months(player_nickname: str):
    player_games_from_last_twelve_months = []
    current_datetime = datetime.now()
    current_year = current_datetime.year
    current_month = current_datetime.month
    i = 0
    while(i < 12):
        current_month = current_month-i
        if(current_month < 1):
            current_month = 12
            current_year = current_year-1
        response = await get_games_from_chess_com(player_nickname, current_year, current_month)
        player_games_from_last_twelve_months.append(response.json().get("games", []))
        i += 1
    return player_games_from_last_twelve_months


async def get_flexzin_force_by_time_control(player_nickname: str):
    player_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(player_nickname)
    )
    flexzin_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(FLEXZIN_NICKNAME)
    )

    player_games_from_last_twelve_months, flexzin_games_from_last_twelve_months = await asyncio.gather(player_task, flexzin_task)
    player_force_by_time_control = calculate_player_force_by_time_control(player_games_from_last_twelve_months, player_nickname)
    flexzin_force_by_time_control = calculate_player_force_by_time_control(flexzin_games_from_last_twelve_months, FLEXZIN_NICKNAME)

    flexzin_force_results_by_time_control = {}
    for time_control, player_force in player_force_by_time_control.items():
        if player_force is not None:
            flexzin_force_results_by_time_control[time_control] = round(player_force_by_time_control[time_control]/flexzin_force_by_time_control[time_control],2)

    return flexzin_force_results_by_time_control

def calculate_player_force_by_time_control(player_games_from_last_twelve_months, player_nickname):
    # organiza os ratings por ritmo
    player_ratings_by_time_control = {
        "rapid": [],
        "blitz": [],
        "bullet": [],
    }

    for month in player_games_from_last_twelve_months: 
        for game in month:     
            player_rating = game["white"]["rating"] if player_nickname.lower() in game["white"]["username"].lower() else game["black"]["rating"]
            if(game["time_class"] in TIME_CONTROLS) and game["rated"] is True:
                player_ratings_by_time_control[game["time_class"]].append(player_rating)

    # resultados finais
    average_ratings_by_time_control = {}
    standard_deviation_by_time_control = {}
    error_margin_by_time_control = {}
    player_force_by_time_control = {}

    for time_control, ratings in player_ratings_by_time_control.items():
        # se vazio → tudo None
        if not ratings:
            average_ratings_by_time_control[time_control] = None
            standard_deviation_by_time_control[time_control] = None
            error_margin_by_time_control[time_control] = None
            player_force_by_time_control[time_control] = None
            continue

        # média
        avg = sum(ratings) / len(ratings)
        average_ratings_by_time_control[time_control] = avg

        # soma dos quadrados
        square_sum = sum((r - avg) ** 2 for r in ratings)

        # desvio padrão (com n-1)
        sd = sqrt(square_sum / (len(ratings) - 1))
        standard_deviation_by_time_control[time_control] = sd

        # margem de erro
        error = Z * (sd / sqrt(len(ratings)))
        error_margin_by_time_control[time_control] = error

        # força
        player_force_by_time_control[time_control] = avg - error

    return player_force_by_time_control

async def main():
    player_nickname = input("Forneça o nome do usuário: ")
    result = await get_flexzin_force_by_time_control(player_nickname)
    has_results = False
    if(result.get("rapid")):
        has_results = True
        print(f"🕒 Rapid: {result["rapid"]}, apresentando {int((result["rapid"]-1.0)*100)}% de {"superioridade" if result["rapid"] > 1.0 else "inferioridade"}.")
    if(result.get("blitz")):
        has_results = True
        print(f"⚡ Blitz: {result["blitz"]}, apresentando {int((result["blitz"]-1.0)*100)}% de {"superioridade" if result["blitz"] > 1.0 else "inferioridade"}.")
    if(result.get("bullet")):
        has_results = True
        print(f"💥 Bullet: {result["bullet"]}, apresentando {int((result["bullet"]-1.0)*100)}% de {"superioridade" if result["bullet"] > 1.0 else "inferioridade"}.")
    if has_results is False:
        print("O jogador não tem partidas rated para comparar com o Flexzin.")
if __name__ == "__main__":
    asyncio.run(main())