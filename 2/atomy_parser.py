import requests
from bs4 import BeautifulSoup
import asyncio
from aiohttp import ClientSession
from aiohttp import client_exceptions
import json

from loguru import logger



class ParserAtomypartners:
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    def __init__(self, url):
        self.logger = logger
        self.logger.add("app.log", level="INFO")
        self.url  = url
        self.session = None

    async def get_soup(self, url):
        try:
            async with self.session.get(url=url, ssl=False) as response:
                if response.ok:
                    return BeautifulSoup(await response.text(), "html.parser")
                return None
        except client_exceptions.ClientConnectorError:
            return None


    def get_cats(self):
        response = requests.get(self.url)
        soup = BeautifulSoup(response.text, 'html.parser')
        cats = soup.find_all('li', class_='wc-block-product-categories-list-item')

        return [cat_tags.find('a').get('href') for cat_tags in cats]

    @staticmethod
    def __get_prod_urls_list(cards_urls):
        all_cards_urls = []
        for lst in cards_urls:
            all_cards_urls += lst
        return all_cards_urls

    async def __get_prod_url(self, url):
        soup = await self.get_soup(url)
        products = soup.find_all('a', class_='woocommerce-LoopProduct-link woocommerce-loop-product__link')
        return [prod_url.get('href') for prod_url in products]


    async def __gather_products_url(self, cats):
        tasks = [asyncio.create_task(self.__get_prod_url(
            cat_url)) for cat_url in cats]
        return await asyncio.gather(*tasks)

    async def __get_prod_info(self, url):
        soup = await self.get_soup(url)
        while not soup:
            soup = await self.get_soup(url)
        if soup:
            list_images = soup.find('div', class_='woocommerce-product-gallery woocommerce-product-gallery--with-images woocommerce-product-gallery--columns-4 images').find_all('a')
            image_urls = tuple([image_url.get('href') for image_url in list_images])
            prod_info = soup.find('div', class_='et_pb_column et_pb_column_1_2 et_pb_column_2 et_pb_css_mix_blend_mode_passthrough et-last-child')
            name_tag = prod_info.find('h1')
            name = name_tag.text if name_tag else prod_info.find('h2').text
            price_info = prod_info.find_all('h3')
            retail_price = price_info[0].find('strong').text
            participant_price = price_info[1].find('strong').text
            if price_info[2].text:
                pv = price_info[2].find('strong').text
            else:
                pv = price_info[3].find('strong').text
            return {url: {
                'Название': name,
                'Розничная цена': retail_price,
                'Цена участника': participant_price,
                'PV': pv if pv != 'PV' or pv != '' else None,
                'Картинки': image_urls
            }}
        return url

    async def __gather_prod_info(self, products):
        tasks = [
            asyncio.create_task(self.__get_prod_info(prod_url))
            for prod_url in products
        ]
        return await asyncio.gather(*tasks)

    async def __get_res(self):
        cats = self.get_cats()
        async with ClientSession(trust_env=True) as session:
            self.session = session
            products = self.__get_prod_urls_list(await self.__gather_products_url(cats))
            info = await self.__gather_prod_info(products)

        with open('res.json', 'w+', encoding='utf-8') as f:
            a = json.dumps(info, indent=4, ensure_ascii=False)
            f.write(a)



    def get_result(self):
        asyncio.run(self.__get_res())