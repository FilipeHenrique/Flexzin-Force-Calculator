import asyncio
import discord
from bot import FlexzinForceBot
from config import DISCORD_TOKEN

async def main():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = FlexzinForceBot(
        command_prefix="!",
        intents=intents
    )

    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())