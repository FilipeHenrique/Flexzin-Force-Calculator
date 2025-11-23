import aiohttp
import asyncio
from datetime import datetime

import requests

CHESS_COM_BASE_URL = "https://api.chess.com"

class ChessComApiClient:
    def get_player_profile_data(self, player_nickname: str):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}"
        headers = {"User-Agent": "flexzin-force/1.0"}
        resp = requests.get(url, headers=headers)
        return resp.json()

    async def get_games_from_chess_com(self, session, player_nickname, year, month):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}/games/{year}/{month}"
        headers = {"User-Agent": "flexzin-force/1.0"}
        
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return data.get("games", [])

    async def get_player_games_from_last_six_months(self, player_nickname: str):
        tasks = []
        now = datetime.now()
        year = now.year
        month = now.month

        months = []
        for _ in range(6):
            months.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        async with aiohttp.ClientSession() as session:
            for y, m in months:
                tasks.append(
                    self.get_games_from_chess_com(session, player_nickname, y, m)
                )

            return await asyncio.gather(*tasks)
