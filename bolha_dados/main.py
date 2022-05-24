from playwright.async_api import Playwright, async_playwright, Page, Locator
from loguru import logger
from dataclasses import dataclass
from typing import List
import os
import asyncio
import time
import urllib.parse

import sys
from subprocess import Popen, PIPE

p = Popen([sys.executable, "-m", "playwright", "install"], stdin=PIPE, stdout=PIPE, stderr=PIPE)


@dataclass
class TwitterBot:
    """
    Some explanation about this bot
    """
    client: Playwright
    cookie_path: str
    query: str
    src_option: str
    from_option: str
    default_wait_time_ms: int
    browser_visible: bool = True

    async def __browser_init(self) -> Page:
        browser = await self.client.chromium.launch(chromium_sandbox=False,
                                                    headless=False)

        context = await browser.new_context(storage_state=self.cookie_path)
        page = await context.new_page()

        full_url = (fr'https://twitter.com/'
                    fr'search?q={self.query}&'
                    fr'src={self.src_option}&'
                    fr'f={self.from_option}')

        await page.goto(full_url)
        await page.wait_for_timeout(self.default_wait_time_ms)

        return page

    async def __is_tweets(self, page: Page) -> bool:
        tot = await page.locator(self.__get_tweets_xpath).count()
        if tot == 0:
            logger.info("Hmmm... There's no new tweet to interact.")
            return False

        return True

    async def __is_not_interacted_tweets(self, page: Locator) -> bool:
        tot = await page.locator(self.__get_tweets_xpath).count()
        if tot == 0:
            logger.info("Hmmm... There's no new tweet to interact.")
            return True

        return False

    @property
    def __get_tweets_xpath(self) -> str:
        return (r'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/'
                r'div[1]/div/div[2]/div/section/div/div/div/div/div/div/'
                r'article')

    async def __interact_tweets(self, page: Page, tweets_locator: Locator, actions: List[str]):

        logger.info(f'Amount Tweets Founded: "{await tweets_locator.count()}"')

        if await self.__is_not_interacted_tweets(tweets_locator):
            tweets_id: List[str] = await self.__find_tweets_id(tweets_locator)

            for t_id in tweets_id:
                event_elements = page.locator(f'article[aria-labelledby="{t_id}"]').locator('div[data-testid]')

                is_new_tweet = True
                for index in range(await event_elements.count()):
                    event_element = event_elements.nth(index)

                    data_testid = await event_element.get_attribute('data-testid')
                    if data_testid == 'like':
                        await event_element.click()
                        break
                    elif data_testid == 'unlike':
                        logger.info('There is not new tweet!!!')
                        is_new_tweet = False

                if not is_new_tweet:
                    break

                await page.wait_for_timeout(1000)

    async def __reload_page(self, page: Page):
        logger.success('Refreshing page ...')
        await page.reload()
        await page.wait_for_timeout(self.default_wait_time_ms)

    @staticmethod
    async def __find_tweets_id(tweets_locator: Locator) -> List[str]:
        tot = await tweets_locator.count()
        tweets_id = []
        for index in range(tot):
            tweet_element = tweets_locator.nth(index)
            tweets_id.append(await tweet_element.get_attribute('aria-labelledby'))

        return tweets_id

    async def __like_tweet(self):
        ...

    async def __retweet_tweet(self):
        ...

    async def run(self):

        page = await self.__browser_init()
        try:
            if await self.__is_tweets(page):
                tweets_locator = page.locator(self.__get_tweets_xpath)
                await self.__interact_tweets(page, tweets_locator, actions=['like', 'retweet'])

            await page.close()
        except Exception as error:
            logger.error(error)


async def main() -> None:
    while True:
        async with async_playwright() as play_wright:
            bolha_dados_bot = TwitterBot(client=play_wright,
                                         cookie_path=os.getenv('COOKIE_PATH'),
                                         query=urllib.parse.quote(os.getenv('TWITTER_QUERY')),
                                         src_option=urllib.parse.quote(os.getenv('SRC_OPTION')),
                                         from_option=urllib.parse.quote(os.getenv('FROM_OPTION')),
                                         default_wait_time_ms=int(os.getenv('DEFAULT_TIME_WAIT_MS')),
                                         browser_visible=bool(os.getenv('BROWSER_VISIBLE')))
            await bolha_dados_bot.run()


if __name__ == '__main__':
    asyncio.run(main())
