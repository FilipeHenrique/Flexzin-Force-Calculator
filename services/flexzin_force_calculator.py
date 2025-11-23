from math import sqrt
from services.chess_com_api_client import ChessComApiClient
import asyncio

FLEXZIN_NICKNAME = "FIexPrime"
TIME_CONTROLS = ["rapid", "blitz", "bullet"]
Z = 1.96

class FlexzinForceCalculator:
    def __init__(self, chess_com_api_client: ChessComApiClient):
        self.chess_com_api_client = chess_com_api_client    

    async def get_flexzin_force_by_time_control(self, player_nickname: str):
        player_task = asyncio.create_task(
            self.chess_com_api_client.get_player_games_from_last_twelve_months(player_nickname)
        )
        flexzin_task = asyncio.create_task(
            self.chess_com_api_client.get_player_games_from_last_twelve_months(FLEXZIN_NICKNAME)
        )

        player_games_from_last_twelve_months, flexzin_games_from_last_twelve_months = await asyncio.gather(player_task, flexzin_task)
        player_force_by_time_control = self.calculate_player_force_by_time_control(player_games_from_last_twelve_months, player_nickname)
        flexzin_force_by_time_control = self.calculate_player_force_by_time_control(flexzin_games_from_last_twelve_months, FLEXZIN_NICKNAME)

        flexzin_force_results_by_time_control = {}
        for time_control, player_force in player_force_by_time_control.items():
            if player_force is not None:
                flexzin_force_results_by_time_control[time_control] = round(player_force_by_time_control[time_control]/flexzin_force_by_time_control[time_control],2)

        return flexzin_force_results_by_time_control

    def calculate_player_force_by_time_control(self, player_games_from_last_twelve_months, player_nickname):
        player_ratings_by_time_control = {time_control: [] for time_control in TIME_CONTROLS}
        for month in player_games_from_last_twelve_months: 
            for game in month:     
                player_rating = game["white"]["rating"] if player_nickname.lower() in game["white"]["username"].lower() else game["black"]["rating"]
                if(game["time_class"] in TIME_CONTROLS) and game["rated"] is True:
                    player_ratings_by_time_control[game["time_class"]].append(player_rating)

        player_force_by_time_control = {}     
        for time_control, ratings in player_ratings_by_time_control.items():
            if not ratings:
                player_force_by_time_control[time_control] = None
                continue
            average_rating = sum(ratings) / len(ratings)
            square_sum = sum((r - average_rating) ** 2 for r in ratings)
            standard_deviation = sqrt(square_sum / (len(ratings) - 1))
            error_margin = Z * (standard_deviation / sqrt(len(ratings)))
            player_force_by_time_control[time_control] = average_rating - error_margin

        return player_force_by_time_control