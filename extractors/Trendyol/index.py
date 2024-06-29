from dataclasses import dataclass
from requestors.trendyol.index import Trendyol_Requestor
from bs4 import BeautifulSoup


@dataclass
class Trendyol_Extractor:
    requestor: Trendyol_Requestor
    requestedNumber: int
    # def requestCount(self):
    #     requestedNumber = input(
    #         f"There are {self.requestor.getItemsCount()} items, how many would you like to get? "
    #     )

    #     while not requestedNumber.isdigit() or int(requestedNumber) > int(
    #         self.requestor.getItemsCount()
    #     ):
    #         requestedNumber = input(
    #             f"Please input a valid number between 1 and {self.requestor.getItemsCount()} "
    #         )

    #     self.requestedNumber = int(requestedNumber)

    # def __post_init__(self):
    #     self.requestCount()

    def __turnToDigit(self, num: str) -> float:
        s = ""
        for i in num:
            if i.isdigit() or i == ".":
                s += i

        return float(s)

    def __extract_alternate_image(self, link: str):
        import requests

        product_page = requests.get(link, cookies=self.requestor.cookies).text
        imageUrl = (
            BeautifulSoup(product_page, "html.parser")
            .find("div", class_="carousel-item")
            .find("img")
            .get("src")
        )
        return imageUrl

    def __extract(self, product: BeautifulSoup, index: int) -> dict:
        result = {}
        # place_holder_url = "https://cdn.dsmcdn.com/mweb/production/product-placeholder.6dd40f981c7c0292fec5160d3b067fbb.jpg"
        try:
            result["imageURL"] = product.find("img").get("src")
            result["brand"] = product.find("span", class_="product-brand").getText()
            result["productName"] = product.find(
                "span", class_="product-name-text"
            ).getText()
            pricesArea = product.find("div", class_="rrp-location-right")
            if pricesArea == None:
                pricesArea = product.find("div", class_="promotion-price-wrapper")
            if pricesArea == None:
                result["discountedPrice"] = product.find(
                    "span", class_="discounted-price"
                ).getText()
                result["currency"] = product.find("span", class_="currency").getText()
            elif len(pricesArea.findChildren(recursive=False)) > 1:
                currency = None
                original = product.find("p", class_="price-text")
                discounted = product.find("p", class_="selling-price with-discount")

                if original == None or discounted == None:
                    original = product.find("div", class_="p-selling-price")
                    discounted = product.find("div", class_="p-discounted-price")
                    currency = discounted.getText().split(" ")[1]
                result["originalPrice"] = original.getText()
                result["discountedPrice"] = discounted.getText()
                result["currency"] = currency
            else:
                result["originalPrice"] = (
                    product.find("p", class_="selling-price").getText().split(" ")[0]
                )

            if "currency" not in result or result["currency"] == None:
                result["currency"] = product.find(
                    "sup", class_="currency-symbol"
                ).getText()
            result["link"] = f'https://trendyol.com{product.find("a").get("href")}'

            if "originalPrice" in result:
                result["originalPrice"] = self.__turnToDigit(result["originalPrice"])
            if "discountedPrice" in result:
                result["discountedPrice"] = self.__turnToDigit(
                    result["discountedPrice"]
                )
            # if result["imageURL"] == place_holder_url:
            #     result["imageURL"] = self.__extract_alternate_image(result["link"])
        except Exception as e:
            print(f"Error in extracting product {index}")
            print(e)
            print(product)

        return result

    def extract_requested_products(self):
        resultSet = []
        i = 1
        while len(resultSet) < self.requestedNumber:
            page_products = self.requestor.extract_page(i)
            bs = BeautifulSoup(page_products, "html.parser")
            page_products = bs.find_all(
                class_="product", attrs={"data-testid": "product-card"}
            )
            if not page_products:
                break
            i += 1
            for index, product in enumerate(page_products):
                resultSet.append(self.__extract(product, index))
                if len(resultSet) == self.requestedNumber:
                    break

        resultSet = [
            dict(product) for product in {tuple(d.items()) for d in resultSet}
        ][: self.requestedNumber]

        return resultSet


    