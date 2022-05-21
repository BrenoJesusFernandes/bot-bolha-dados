from playwright.sync_api import Playwright, sync_playwright
import urllib.parse
from loguru import logger


def run(play_wright: Playwright) -> None:
    """
    Just runs everything
    :param play_wright: client
    :return: None
    """
    browser = play_wright.chromium.launch(headless=False)

    # Load cookie
    context = browser.new_context(storage_state='auth.json')
    page = context.new_page()

    # Parameters of url
    query = urllib.parse.quote_plus('@BolhaDados')
    src_option = urllib.parse.quote_plus('typed_query')
    twitter_url = 'https://twitter.com'
    from_option = urllib.parse.quote_plus('live')

    full_url = fr'{twitter_url}/search?q={query}&src={src_option}&f={from_option}'
    page.goto(full_url)
    page.wait_for_timeout(5000)

    while True:
        tweet_xpath = (r'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/'
                       r'div[1]/div/div[2]/div/section/div/div/div/div/div/div/article')

        if page.locator(tweet_xpath).count() == 0:
            logger.info('Pagina vazia!!!')
            page.reload()
            page.wait_for_timeout(5000)
            continue

        tweets = page.locator(tweet_xpath)
        logger.info(f'Quantidade Tweets Encontrados: "{tweets.count()}"')

        tweets_id = []
        for index in range(tweets.count()):
            tweet = tweets.nth(index)
            tweets_id.append(tweet.get_attribute('aria-labelledby'))

        for t_id in tweets_id:
            event_elements = page.locator(f'article[aria-labelledby="{t_id}"]').locator('div[data-testid]')

            is_new_tweet = True
            for index in range(event_elements.count()):
                event_element = event_elements.nth(index)

                if event_element.get_attribute('data-testid') == 'like':
                    event_element.click()
                    break
                elif event_element.get_attribute('data-testid') == 'unlike':
                    logger.info('Nenhum Tweet Novo Encontrado!!!')
                    is_new_tweet = False

            if not is_new_tweet:
                break

            page.wait_for_timeout(1000)

        logger.success('Todos filtros aplicados!')
        page.reload()
        page.wait_for_timeout(5000)

    page.screenshot(path='xablau.png')
    context.close()
    browser.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)
