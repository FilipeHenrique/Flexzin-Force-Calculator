import asyncio
import discord
import psutil
import threading
import time
from bot import FlexzinForceBot
from config import DISCORD_TOKEN


def monitor_ram(interval=5):
    process = psutil.Process()
    while True:
        mem = process.memory_info().rss / (1024 * 1024)
        print(f"[RAM] Uso atual: {mem:.2f} MB")
        time.sleep(interval)


async def main():
    threading.Thread(target=monitor_ram, daemon=True).start()

    intents = discord.Intents.default()
    intents.message_content = True

    bot = FlexzinForceBot(
        command_prefix="!",
        intents=intents
    )

    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())