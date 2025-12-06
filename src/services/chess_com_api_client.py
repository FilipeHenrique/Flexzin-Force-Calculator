import os
import aiohttp
import asyncio
from datetime import datetime

import requests

from config import CHESS_COM_BASE_URL, MONTHS_QUANTITY_TO_GET_GAMES_FROM

class ChessComApiClient:
    def __init__(self):
        self.flexzin_nickname = os.getenv("FLEXZIN_NICKNAME", "")
        self.session = None #aiohttp limitation, needed to implement an init method
        
    async def init(self):
        self.session = aiohttp.ClientSession()
        
    def get_player_profile_data(self, player_nickname: str):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}"
        headers = {"User-Agent": "flexzin-force/1.0"}
        resp = requests.get(url, headers=headers)
        if resp.status_code == 404:
            return None
        return resp.json()

    async def get_games_from_chess_com(self, session, player_nickname, year, month):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}/games/{year}/{month}"
        headers = {"User-Agent": "flexzin-force/1.0"}
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return data.get("games", [])

    async def get_player_games_from_last_months(self, player_nickname: str):
        tasks = []
        now = datetime.now()
        year = now.year
        month = now.month

        months = []
        for _ in range(MONTHS_QUANTITY_TO_GET_GAMES_FROM):
            months.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1

        for y, m in months:
            month_str = f"{m:02d}"  # garante 2 dígitos, necessário pra API do chess.com
            tasks.append(
                self.get_games_from_chess_com(self.session, player_nickname, y, month_str)
            )

        return await asyncio.gather(*tasks)

    async def get_flexzin_status(self):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{self.flexzin_nickname}/stats"
        headers = {"User-Agent": "flexzin-force/1.0"}
        async with self.session.get(url, headers=headers) as resp:
            return await resp.json()
        
    async def close_session(self):
        await self.session.close()
