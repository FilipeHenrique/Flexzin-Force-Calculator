import requests
from datetime import datetime
import asyncio

FLEXZIN_NICKNAME = "FlexPrime"
Z = 1.96

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
        response = get_games_from_chess_com(player_nickname, current_year, current_month)
        player_games_from_last_twelve_months.append(response)
        i += 1
    print(len(player_games_from_last_twelve_months))
    return player_games_from_last_twelve_months

 # TO DO, FAZER SER DE FATO ASYNC, REQUESTS BLOQUEIA A THREAD
async def get_games_from_chess_com(player_nickname, current_year, current_month):
    # header to avoid cloudflare blocking
    headers = {"User-Agent": "flexzin-force/1.0"}
    response = requests.get(f"https://api.chess.com/pub/player/{player_nickname}/games/{current_year}/{current_month}", headers=headers)
    return response


async def calculate_flexzin_force(player_nickname: str):
    player_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(player_nickname)
    )
    flexzin_task = asyncio.create_task(
        get_player_games_from_last_twelve_months(FLEXZIN_NICKNAME)
    )

    player_games_from_last_twelve_months, flexzin_games_from_last_twelve_months = await asyncio.gather(player_task, flexzin_task)

    # codar aqui os cálculos matemáticos

    return # retorno do flexzin force

async def main():
    player_nickname = input("Forneça o nome do usuário: ")
    await calculate_flexzin_force(player_nickname)

if __name__ == "__main__":
    asyncio.run(main())