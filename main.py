from math import sqrt
import requests
from datetime import datetime
import asyncio

# TO DO
    # LEMBRAR DE CONSIDERAR APENAS PARTIDAS RATED
    # AJUSTAR OS DICIONÁRIOS PRA PREENCHER BASEADO NO CONST TIME_CONTROLS PRA EVITAR REPETIÇÃO DE CÓDIGO


FLEXZIN_NICKNAME = "FIexPrime"
Z = 1.96
TIME_CONTROLS = ["rapid", "blitz", "bullet"]

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

 # TO DO, FAZER SER DE FATO ASYNC, REQUESTS BLOQUEIA A THREAD
async def get_games_from_chess_com(player_nickname, current_year, current_month):
    # header to avoid cloudflare blocking
    headers = {"User-Agent": "flexzin-force/1.0"}
    response = requests.get(f"https://api.chess.com/pub/player/{player_nickname}/games/{current_year}/{current_month}", headers=headers)
    return response


async def calculate_flexzin_force_by_time_control(player_nickname: str):
    player_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(player_nickname)
    )
    flexzin_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(FLEXZIN_NICKNAME)
    )

    player_games_from_last_twelve_months, flexzin_games_from_last_twelve_months = await asyncio.gather(player_task, flexzin_task)
    player_force_by_time_control = get_player_force_by_time_control(player_games_from_last_twelve_months, player_nickname)
    flexzin_force_by_time_control = get_player_force_by_time_control(flexzin_games_from_last_twelve_months, FLEXZIN_NICKNAME)

    flexzin_force_results_by_time_control = {
        "rapid": player_force_by_time_control["rapid"]/flexzin_force_by_time_control["rapid"],
        "blitz": player_force_by_time_control["blitz"]/flexzin_force_by_time_control["blitz"],
        "bullet": player_force_by_time_control["bullet"]/flexzin_force_by_time_control["bullet"],
    }

    return flexzin_force_results_by_time_control

def get_player_force_by_time_control(player_games_from_last_twelve_months, player_nickname):
    # organiza os ratings por ritmo
    player_ratings_by_time_control = {
        "rapid": [],
        "blitz": [],
        "bullet": [],
    }

    for month in player_games_from_last_twelve_months: 
        for game in month:     
            player_rating = game["white"]["rating"] if player_nickname.lower() in game["white"]["@id"].lower() else game["black"]["rating"]
            if(game["time_class"] in TIME_CONTROLS) and game["rated"] is True:
                player_ratings_by_time_control[game["time_class"]].append(player_rating)

    # calcula a média dos ratings
    average_ratings_by_time_control = {
        time_control: (sum(rating)/len(rating) if rating else None)
        for time_control, rating in player_ratings_by_time_control.items()
    }

    # calcula a soma da diferença dos quadrados do rating, por ritmo
    square_differences_sum_by_time_control = {
        "rapid": 0,
        "blitz": 0,
        "bullet": 0
    }
    for time_control in player_ratings_by_time_control.keys():
        for rating in player_ratings_by_time_control[time_control]:
            square_differences_sum_by_time_control[time_control] = square_differences_sum_by_time_control[time_control] + pow(rating - average_ratings_by_time_control[time_control], 2)

    standard_deviation_by_time_control = {
        "rapid": sqrt(square_differences_sum_by_time_control["rapid"]/len(player_ratings_by_time_control["rapid"])-1),
        "blitz": sqrt(square_differences_sum_by_time_control["blitz"]/len(player_ratings_by_time_control["blitz"])-1),
        "bullet": sqrt(square_differences_sum_by_time_control["bullet"]/len(player_ratings_by_time_control["bullet"])-1),
    }

    error_margin_by_time_control = {
        "rapid":  Z * (standard_deviation_by_time_control["rapid"]/sqrt(len(player_ratings_by_time_control["rapid"]))),
        "blitz": Z * (standard_deviation_by_time_control["blitz"]/sqrt(len(player_ratings_by_time_control["blitz"]))),
        "bullet": Z * (standard_deviation_by_time_control["bullet"]/sqrt(len(player_ratings_by_time_control["bullet"])))
    }

    player_force_by_time_control = {
        "rapid": average_ratings_by_time_control["rapid"] - error_margin_by_time_control["rapid"],
        "blitz": average_ratings_by_time_control["blitz"] - error_margin_by_time_control["blitz"],
        "bullet": average_ratings_by_time_control["bullet"] - error_margin_by_time_control["bullet"]
    }

    return player_force_by_time_control

async def main():
    player_nickname = input("Forneça o nome do usuário: ")
    result = await calculate_flexzin_force_by_time_control(player_nickname)
    print("Rapid: ", result["rapid"])
    print("Blitz: ", result["blitz"])
    print("Bullet: ", result["bullet"])

if __name__ == "__main__":
    asyncio.run(main())