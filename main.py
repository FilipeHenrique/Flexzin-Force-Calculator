from services.flexzin_force_calculator import FlexzinForceCalculator
from services.chess_com_api_client import ChessComApiClient
import asyncio

async def main():
    player_nickname = input("Forneça o nome do usuário: ")
    chess_com_api_client = ChessComApiClient()
    flexzin_force_calculator = FlexzinForceCalculator(chess_com_api_client= chess_com_api_client)
    result = await flexzin_force_calculator.get_flexzin_force_by_time_control(player_nickname)
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