from math import sqrt
import os

from services.redis_service import RedisService
from services.chess_com_api_client import ChessComApiClient
import json

TIME_CONTROLS = ["rapid", "blitz", "bullet"]
HOUR_IN_SECONDS = 3600
Z = 1.96

class FlexzinForceCalculator:
    def __init__(self, chess_com_api_client: ChessComApiClient, redis_repository: RedisService):
        self.chess_com_api_client = chess_com_api_client    
        self.redis_repository = redis_repository
        self.flexzin_nickname = os.getenv("FLEXZIN_NICKNAME", "")

    async def get_flexzin_force_by_time_control(self, player_nickname: str):
        cached_flexzin_force = await self.redis_repository.get(self.flexzin_nickname)
        cached_player_force = await self.redis_repository.get(player_nickname)
        if((cached_flexzin_force)):
            flexzin_force_by_time_control = json.loads((cached_flexzin_force))
        else:
            flexzin_games_from_last_six_months = await self.chess_com_api_client.get_player_games_from_last_months(self.flexzin_nickname)
            flexzin_force_by_time_control = self.calculate_player_force_by_time_control(flexzin_games_from_last_six_months, self.flexzin_nickname)
            await self.redis_repository.set(self.flexzin_nickname, json.dumps(flexzin_force_by_time_control), expire= HOUR_IN_SECONDS)

        if(cached_player_force):
            player_force_by_time_control = json.loads(cached_player_force)
        else:
            player_games_from_last_months = await self.chess_com_api_client.get_player_games_from_last_months(player_nickname)
            player_force_by_time_control = self.calculate_player_force_by_time_control(player_games_from_last_months, player_nickname)
            await self.redis_repository.set(player_nickname, json.dumps(player_force_by_time_control), expire= HOUR_IN_SECONDS)         

        flexzin_force_results_by_time_control = {}
        for time_control, player_force in player_force_by_time_control.items():
            if player_force is not None:
                flexzin_force_results_by_time_control[time_control] = round(player_force_by_time_control[time_control]/flexzin_force_by_time_control[time_control],2)

        return flexzin_force_results_by_time_control

    def calculate_player_force_by_time_control(self, player_games_from_last_months, player_nickname):
        player_ratings_by_time_control = {time_control: [] for time_control in TIME_CONTROLS}
        for month in player_games_from_last_months: 
            for game in month:     
                if(game["time_class"] in TIME_CONTROLS) and game["rated"] is True:
                    player_rating = game["white"]["rating"] if player_nickname.lower() in game["white"]["username"].lower() else game["black"]["rating"]
                    player_ratings_by_time_control[game["time_class"]].append(player_rating)

        player_force_by_time_control = {}     
        for time_control, ratings in player_ratings_by_time_control.items():
            if not ratings:
                player_force_by_time_control[time_control] = None
                continue
            average_rating = sum(ratings) / len(ratings)
            square_sum = sum((r - average_rating) ** 2 for r in ratings)
            standard_deviation = sqrt(square_sum / max(len(ratings) - 1, 1))
            error_margin = Z * (standard_deviation / sqrt(len(ratings)))
            player_force_by_time_control[time_control] = average_rating - error_margin

        return player_force_by_time_control