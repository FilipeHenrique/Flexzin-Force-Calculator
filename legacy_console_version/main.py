import asyncio
from services.flexzin_force_calculator import FlexzinForceCalculator
from services.chess_com_api_client import ChessComApiClient
from services.redis_service import RedisService

async def main():
    player_nickname = input("Forneça o nome do usuário: ")
    chess_com_api_client = ChessComApiClient()
    redis_repository = RedisService()
    flexzin_force_calculator = FlexzinForceCalculator(chess_com_api_client, redis_repository)
    result = await flexzin_force_calculator.get_flexzin_force_by_time_control(player_nickname)
    icons = {
        "rapid": "🕒 Rapid",
        "blitz": "⚡ Blitz",
        "bullet": "💥 Bullet",
    }

    has_results = False
    for time_control, label in icons.items():
        value = result.get(time_control)

        if not value:
            continue

        has_results = True

        if value > 1.0:
            status = "superioridade"
            percent = abs(int((value - 1.0) * 100))
        elif value < 1.0:
            status = "inferioridade"
            percent = abs(int((value - 1.0) * 100))
        else:
            status = "igualdade"
            percent = 0

        if(status == "igualdade"):
            print(
                f"{label}: {value}, "
                f"apresentando igualdade."
            )
        else:    
            print(
                f"{label}: {value}, "
                f"apresentando {percent}% de {status}."
            )

    if not has_results:
        print("O jogador não tem partidas rated para comparar com o Flexzin.")

    await redis_repository.close()
        
if __name__ == "__main__":
    asyncio.run(main())