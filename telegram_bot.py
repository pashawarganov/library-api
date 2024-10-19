import asyncio
import logging
import sys
from os import getenv

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv()
TOKEN = getenv("BOT_TOKEN")
CHAT_ID = getenv("CHAT_ID")

if not TOKEN or not CHAT_ID:
    logging.error("BOT_TOKEN or CHAT_ID not provided")
    sys.exit("Please check .env file.")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

dp.include_router(router)


async def send_borrowing_notification(message: str) -> None:
    """
    Func to send messages to telegram
    """
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
    except Exception as e:
        logging.error(f"Failed to send message: {e}")


async def main() -> None:
    """
    Main func to run dispatcher
    """
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
