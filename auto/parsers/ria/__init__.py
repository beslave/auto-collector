import asyncio
import aiohttp

from bs4 import BeautifulSoup


class Parser(object):
    BASE_LIST_PAGE = 'https://auto.ria.com/newauto_blocks/search?t=newdesign/search/search&limit=100'

    def __init__(self):
        self.current_page_url = self.BASE_LIST_PAGE
        self.number = 0
        self.adv_iterator = None

    def iter_pages(self):
        pass

    def iter_advertisements(self, soup):
        for adv_element in soup.select('.ticket-item-newauto'):
            name_element = adv_element.select('.name a')[0]
            year_element = adv_element.select('.year')[0]
            price_element = adv_element.select('.block-price strong')[0]
            photo_element = adv_element.select('.block-photo img')[0]

            yield {
                'url': name_element.attrs['href'],
                'name': name_element.text.strip(),
                'year': int(year_element.text.strip()),
                'price': price_element.text.strip(),
                'autosalon_id': name_element.attrs.get('autosalon_id'),
                'marka_id': name_element.attrs.get('marka_id'),
                'model_id': name_element.attrs.get('model_id'),
                'complectation_id': name_element.attrs.get('complete_id'),
                'advertisement_id': name_element.attrs.get('auto_id'),
            }

    async def parse_advertisement(self, adv):
        self.number += 1
        return self.number

    async def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.current_page_url:
            raise StopAsyncIteration

        if not self.adv_iterator:
            with aiohttp.ClientSession() as session:
                with aiohttp.Timeout(10):
                    async with session.get(self.current_page_url) as response:
                        list_html = await response.read()
                        soup = BeautifulSoup(list_html, 'html.parser')
                        self.adv_iterator = self.iter_advertisements(soup)
                        next_link = soup.select('.pagination .show-more.fl-r')
                        if next_link:
                            next_page = next_link[0].attrs['page']
                            self.current_page_url = self.BASE_LIST_PAGE + '&page=' + next_page
                        else:
                            self.current_page_url = None

        try:
            return self.adv_iterator.__next__()
        except StopIteration:
            self.adv_iterator = None
            return await self.__anext__()
