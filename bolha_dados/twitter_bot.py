from playwright.async_api import Playwright, Page, Locator, StorageState
from dataclasses import dataclass
from typing import List
from loguru import logger


@dataclass
class TwitterBot:
    """
    Some explanation about this bot
    """
    client: Playwright
    cookie_path: StorageState
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
                    if data_testid == 'retweet':
                        logger.info('Retwitando ...')
                        await event_element.click()
                        await page.locator('[data-testid="retweetConfirm"]').click()
                        break
                    elif data_testid == 'unretweet':
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

    async def retweet_last(self):

        page = await self.__browser_init()

        if await self.__is_tweets(page):
            tweets_locator = page.locator(self.__get_tweets_xpath)
            await self.__interact_tweets(page, tweets_locator, actions=['like', 'retweet'])

        await page.close()

