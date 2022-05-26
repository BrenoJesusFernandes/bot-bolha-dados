import os

from playwright.async_api import async_playwright, StorageState
from bolha_dados.twitter_bot import TwitterBot
from loguru import logger
import asyncio
import urllib.parse
import requests


async def default_task(cookie: StorageState):
    """
    Some comment here
    """
    while True:
        try:
            async with async_playwright() as play_wright:
                bolha_dados_bot = TwitterBot(client=play_wright,
                                             cookie_path=cookie,
                                             query=urllib.parse.quote(os.getenv('TWITTER_QUERY')),
                                             src_option=urllib.parse.quote(os.getenv('SRC_OPTION')),
                                             from_option=urllib.parse.quote(os.getenv('FROM_OPTION')),
                                             default_wait_time_ms=int(os.getenv('DEFAULT_TIME_WAIT_MS')),
                                             browser_visible=bool(os.getenv('BROWSER_VISIBLE')))
                await bolha_dados_bot.retweet_last()

        except Exception as error:
            logger.error(error)


async def main() -> None:
    with requests.get(url=os.getenv('COOKIE_URL')) as resp:

        if resp.status_code == 200:
            await default_task(StorageState(resp.json()))
        else:
            logger.error('Error to download the cookie!')

if __name__ == '__main__':
    asyncio.run(main())
