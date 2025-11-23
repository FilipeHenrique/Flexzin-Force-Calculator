import aiohttp
import asyncio
from datetime import datetime

CHESS_COM_BASE_URL = "https://api.chess.com"

class ChessComApiClient:
    async def get_games_from_chess_com(self, session, player_nickname, year, month):
        url = f"{CHESS_COM_BASE_URL}/pub/player/{player_nickname}/games/{year}/{month}"
        headers = {"User-Agent": "flexzin-force/1.0"}
        
        async with session.get(url, headers=headers) as resp:
            data = await resp.json()
            return data.get("games", [])

    async def get_player_games_from_last_twelve_months(self, player_nickname: str):
        tasks = []
        now = datetime.now()
        year = now.year
        month = now.month

        # gera a lista (ano, mês) dos últimos 12 meses corretamente
        months = []
        for _ in range(12):
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
