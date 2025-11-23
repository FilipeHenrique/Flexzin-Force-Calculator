import requests
from datetime import datetime

# TODO: Armazenar os gets dos 12 meses em tasks (aihttp provavelmente) e fazer as requests serem async, fazendo os 12 meses em paralelo

CHESS_COM_BASE_URL = "https://api.chess.com"

class ChessComApiClient():
    async def get_games_from_chess_com(self, player_nickname, current_year, current_month):
        headers = {"User-Agent": "flexzin-force/1.0"}
        response = requests.get(f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}/games/{current_year}/{current_month}", headers=headers)
        return response

    async def get_player_games_from_last_twelve_months(self, player_nickname: str):
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
            response = await self.get_games_from_chess_com(player_nickname, current_year, current_month)
            player_games_from_last_twelve_months.append(response.json().get("games", []))
            i += 1
        return player_games_from_last_twelve_months