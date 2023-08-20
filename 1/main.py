import contextlib
import requests
from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession
from aiohttp import client_exceptions
import datetime
from math import floor

URL = 'https://www.realitica.com/index.php?for=Prodaja&opa=Budva&type%5B%5D=&type%5B%5D=Apartment&price-min=30000&price-max=150000&since-day=p-anytime&qry=&lng=hr'

DOMAIN = 'https://www.realitica.com'


def time_of_function(function):
    def wrapped(*args):
        start_time = datetime.datetime.now()
        res = function(*args)
        print(datetime.datetime.now() - start_time)
        return res
    return wrapped


async def get_soup(url, session):
    async with session.get(url=url) as response:
        return BeautifulSoup(await response.text(), "html.parser")


async def get_urls_from_cards(url: str, session):
    soup = await get_soup(url, session)
    urls = []

    href_class_lst = soup.find_all('a')
    for a_class in href_class_lst:
        try:
            if a_class.text == 'Detaljno':
                urls.append(a_class.get('href'))
        except:
            print(url, a_class, sep='\n')
    return urls


async def get_profile(url: str, session):
    soup = await get_soup(url, session)
    try:
        profiles_links = soup.find('div', id='aboutAuthor').find_all('a')

        for link in profiles_links:
            link = link.get('href')
            if 'https://' not in link and 'http://' not in link:
                profile_url = DOMAIN + link
                with contextlib.suppress(client_exceptions.ClientConnectorError):
                    if (await session.get(profile_url)).status == 200:
                        return profile_url
    except AttributeError:
        return None


async def get_result_urls(profile_url, session):

    if profile_url and DOMAIN in profile_url:
        url = profile_url
        soup = await get_soup(url, session)

        cards = soup.find_all('div', class_='thumb_div')
        if 0 < len(cards) <= 5:
            return url


async def gather_profiles(cards_urls, session):
    tasks = [asyncio.create_task(get_profile(url, session))
             for url in cards_urls]
    return await asyncio.gather(*tasks)


async def gather_success_profiles(profiles, session):
    tasks = [asyncio.create_task(get_result_urls(
        profile_url, session)) for profile_url in profiles]
    return await asyncio.gather(*tasks)


async def gather_urls_from_cards(cards_urls, session):
    tasks = [asyncio.create_task(get_urls_from_cards(
        url, session)) for url in cards_urls]
    return await asyncio.gather(*tasks)


def get_clean_res(res: list):
    return [url for url in res if url]


def get_max_page(url: str):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    count_cards_list = soup.find('div', style='padding:5px;').find(
        'span').find_all('strong')
    cards_on_page = 20
    max_cards = int(count_cards_list[1].text)
    return floor(max_cards / cards_on_page)


async def get_res():
    URL = 'https://www.realitica.com/index.php?cur_page={}&for=Prodaja&opa=Budva&type%5B%5D=&type%5B%5D=Apartment&price-min=30000&price-max=150000&since-day=p-anytime&qry=&lng=hr'

    max_page = get_max_page(URL.format(0))
    urls = [URL.format(page) for page in range(max_page + 1)]

    async with ClientSession() as session:
        cards_urls = await gather_urls_from_cards(urls, session)
        all_cards_urls = []
        for lst in cards_urls:
            all_cards_urls += lst
        profiles = set(await gather_profiles(all_cards_urls, session))
        result = await gather_success_profiles(profiles, session)

    clean = get_clean_res(result)
    return set(clean)


@time_of_function
def main():
    print(asyncio.run(get_res()))


if __name__ == '__main__':
    # start_time = datetime.datetime.now()
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
    # print(datetime.datetime.now() - start_time)
