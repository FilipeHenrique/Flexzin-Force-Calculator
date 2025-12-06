from discord.ext import commands
from services.chess_com_api_client import ChessComApiClient
from services.flexzin_force_calculator import FlexzinForceCalculator
from services.redis_service import RedisService

class FlexzinForceBot(commands.Bot):
    async def setup_hook(self):
        self.chess_com_api_client = ChessComApiClient()
        await self.chess_com_api_client.init()

        self.redis_repository = RedisService()
        self.flexzin_force_calculator = FlexzinForceCalculator(
            self.chess_com_api_client,
            self.redis_repository
        )

        for ext in [
            "cogs.flexzin_status_cog",
            "cogs.flexzin_force_cog",
        ]:
            await self.load_extension(ext)

        await self.tree.sync()
        print("Slash commands sincronizados.")

    async def close(self):
        await self.redis_repository.close()
        await self.chess_com_api_client.close_session()
        await super().close()

