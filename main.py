import time

from playwright.sync_api import Playwright, sync_playwright, expect, StorageState
import urllib.parse


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
    query = urllib.parse.quote_plus('#CienciaDeDados')
    src_option = urllib.parse.quote_plus('typed_query')
    twitter_url = 'https://twitter.com'
    from_option = urllib.parse.quote_plus('live')

    full_url = fr'{twitter_url}/search?q={query}&src={src_option}&f={from_option}'

    page.goto(full_url)

    page.wait_for_timeout(5000)

    tweets = page.locator(r'//*[@id="react-root"]/div/div/div[2]/main/div/div/div/'
                          r'div[1]/div/div[2]/div/section/div/div/div/div/div/div/article')

    print('Start: ', tweets.count())

    for index in range(8):
        # Get a tweet
        tweet = tweets.nth(index)

        # Click in Like
        tweet.locator('div[data-testid="like"]').click()

        # Click in retweet
        # tweet.locator('div[data-testid="retweet"]').click()
        # page.locator('div[data-testid="retweetConfirm"]').click()

        time.sleep(1)
        print('Middle: ', index, tweets.count())

    print('Final: ', tweets.count())

    page.wait_for_timeout(10 ** 5)

    page.screenshot(path='xablau.png')
    context.close()
    browser.close()


if __name__ == '__main__':
    with sync_playwright() as playwright:
        run(playwright)
