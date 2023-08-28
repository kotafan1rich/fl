import contextlib
import requests
from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession
from aiohttp import client_exceptions
from math import floor
from loguru import logger


class ParserRealitica:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    def __init__(self, url, domain):
        self.logger = logger
        self.logger.add("app.log", level="INFO")
        self.url = url
        self.domain = domain
        self.session = None

    @staticmethod
    def _get_max_page(url):
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        count_cards_list = soup.find('div', style='padding:5px;').find(
            'span').find_all('strong')
        cards_on_page = 20
        max_cards = int(count_cards_list[1].text)
        return floor(max_cards / cards_on_page)

    async def _get_soup(self, url):
        async with self.session.get(url=url) as response:
            return BeautifulSoup(await response.text(), "html.parser")

    async def _get_urls_from_card(self, url):
        soup = await self._get_soup(url)
        urls = []

        href_class_lst = soup.find_all('a')
        for a_class in href_class_lst:
            try:
                if a_class.text == 'Detaljno':
                    urls.append(a_class.get('href'))
            except Exception as ex:
                logger.error(
                    f'{ex}: Ссылка на одну из карточек была не найдена {url}')
        return urls
    async def gather_urls_from_cards(self, urls):
        tasks = [asyncio.create_task(self._get_urls_from_card(url)) for url in urls]
        return await asyncio.gather(*tasks)

    @staticmethod
    def get_cards_urls_list(cards_urls):
        all_cards_urls = []
        for lst in cards_urls:
            all_cards_urls += lst
        return all_cards_urls

    async def _get_profile(self, url: str):
        soup = await self._get_soup(url)
        try:
            profiles_links = soup.find('div', id='aboutAuthor').find_all('a')

            for link in profiles_links:
                link = link.get('href')
                if 'https://' not in link and 'http://' not in link:
                    profile_url = self.domain + link
                    with contextlib.suppress(client_exceptions.ClientConnectorError):
                        if (await self.session.get(profile_url)).status == 200:
                            return profile_url
        except AttributeError:
            logger.error(f'Профиль не найден {url.split("&")[0]}')
            return None

    async def _get_result_urls(self, profile_url):

        if profile_url and self.domain in profile_url:
            url = profile_url
            soup = await self._get_soup(url)

            cards = soup.find_all('div', class_='thumb_div')
            if 0 < len(cards) <= 5:
                return url

    async def gather_profiles(self, cards_urls):
        tasks = [asyncio.create_task(self._get_profile(url)) for url in cards_urls]
        return await asyncio.gather(*tasks)

    async def gather_success_profiles(self, profiles):
        tasks = [asyncio.create_task(self._get_result_urls(
            profile_url)) for profile_url in profiles]
        return await asyncio.gather(*tasks)

    @staticmethod
    def get_clean_res(res):
        return [url for url in res if url]

    async def _get_res(self):
        max_page = self._get_max_page(self.url)
        self.logger.info(f'Кол-во страниц {max_page + 1}')
        self.url += '&cur_page={}'
        urls = [self.url.format(page) for page in range(max_page + 1)]
        logger.success('Ссылки на страницы получены')

        async with ClientSession() as session:
            self.session = session
            cards_urls = await self.gather_urls_from_cards(urls)
            logger.success('Ссылки на каточки со страниц получены')
            all_cards_urls = self.get_cards_urls_list(cards_urls)
            profiles = set(await self.gather_profiles(all_cards_urls))
            logger.success('Ссылки на профили получены')
            result = await self.gather_success_profiles(profiles)
            logger.success('Результаты получены')

            clean = self.get_clean_res(result)
            return set(clean)

    def get_result(self):
        return asyncio.run(self._get_res())


