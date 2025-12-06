from dotenv import load_dotenv
import os

load_dotenv()
MONTHS_QUANTITY_TO_GET_GAMES_FROM = int(os.getenv("MONTHS_QUANTITY_TO_GET_GAMES_FROM", 6))
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FLEXZIN_NICKNAME = os.getenv("FLEXZIN_NICKNAME", "")
CHESS_COM_BASE_URL = os.getenv("CHESS_COM_BASE_URL", "https://api.chess.com")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)