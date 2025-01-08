from dataclasses import dataclass
import requests,aiohttp,asyncio
from bs4 import BeautifulSoup


@dataclass
class Trendyol_Requestor:
    target_country: str
    search_word: str

    def __set_cookies(self):
        countries = requests.get(
            "https://cdn.dsmcdn.com/sfint/production/countries_1708681978450.json"
        ).json()
        selectedCountry = next(
            country
            for country in countries
            if country["name"].lower() == self.target_country
        )
        self.cookies = {
            "language": selectedCountry["language"],
            "countryCode": selectedCountry["code"],
            "storefrontId": selectedCountry["storefrontId"],
            "platform": "web",
        }

    def get_search_word(self) -> str:
        return self.search_word

    def __construct_url(self, index: int) -> str:
        slug_word = self.search_word.replace(" ", "+")
        return f"https://www.trendyol.com/en/sr?st={slug_word}&os=1&q={slug_word}&qt={slug_word}&pi={index}"

    def getItemsCount(self) -> int:
        res = requests.get(self.__construct_url(1), cookies=self.cookies)
        with open("test.html", "w") as f:
            f.write(res.text)
        bs = BeautifulSoup(res.text, "html.parser")
        return bs.find("div", class_="title-text").getText().split(" ")[0].replace('.','')

    def __post_init__(self):
        self.get_search_word()
        self.target_country = self.target_country.lower()
        self.__set_cookies()
        if self.target_country == "turkey":
            print("Turkey is not supported yet...")
        self.session = requests.Session()
        # self.asession= aiohttp.ClientSession(cookies=self.cookies)

    
    
    def extract_page(self, page_index: int) -> str:
        return self.session.get(
            self.__construct_url(page_index), cookies=self.cookies
        ).text
    

    async def get_url(self,session,page_index: int,semaphore:asyncio.Semaphore):
        async with semaphore:
            res=await asyncio.create_task(session.get(self.__construct_url(page_index)))
            if res.status!=200:
                print(f'Index: {page_index},{res.status}')
            res=await res.read()
            await asyncio.sleep(0.5)
            return res.decode()
    

    async def extract_pages_async(self, page_indices: list[int]):
        reqs=[]
        print(len(page_indices))
        async with aiohttp.ClientSession(cookies=self.cookies) as asession:
            sem=asyncio.Semaphore(50)
            for page_index in page_indices:
                reqs.append(asyncio.create_task(self.get_url(asession,page_index,sem)))
            responses = await asyncio.gather(*reqs)
        return responses

    def extract_link(self, link):
        return self.session.get(link, cookies=self.cookies).text

    def __extract_content_id(self, link):
        import re

        regex = r"\d+\?"
        return re.findall(regex, link)[0].removesuffix("?")

    def get_product_details(self, link):
        return self.session.get(
            f"https://public-mdc.trendyol.com/discovery-sfint-product-service/api/product-detail/?contentId={self.__extract_content_id(link)}",
            cookies=self.cookies,
        ).json()

    def get_product_customizable_attrs(self, productGroupID):
        return self.session.get(
            f"https://public.trendyol.com/discovery-sfint-search-service/api/search/slicing-attributes/{productGroupID}",
            cookies=self.cookies,
        ).json()
    
    async def aget_product_details(self,link,session):
        response=await session.get(
            f"https://public-mdc.trendyol.com/discovery-sfint-product-service/api/product-detail/?contentId={self.__extract_content_id(link)}",
            cookies=self.cookies,
        )
        # print(response.status)
        return await response.json()
    
    async def aget_products_details(self,links):
        reqs=[]
        async with aiohttp.ClientSession(cookies=self.cookies) as asession:
            for link in links:
                reqs.append(asyncio.create_task(self.aget_product_details(link,asession)))
            responses = await asyncio.gather(*reqs)
        return responses
