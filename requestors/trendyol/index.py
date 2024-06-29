from dataclasses import dataclass
import requests
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
        bs = BeautifulSoup(res.text, "html.parser")
        return bs.find("div", class_="title").find("p").getText().split(" ")[0]

    def __post_init__(self):
        self.get_search_word()
        self.target_country = self.target_country.lower()
        self.__set_cookies()
        if self.target_country == "turkey":
            print("Turkey is not supported yet...")
        self.session = requests.Session()

    def extract_page(self, page_index: int) -> str:
        return self.session.get(
            self.__construct_url(page_index), cookies=self.cookies
        ).text
