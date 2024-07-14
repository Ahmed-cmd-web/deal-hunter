from dataclasses import dataclass
from requestors.trendyol.index import Trendyol_Requestor
from bs4 import BeautifulSoup


@dataclass
class Trendyol_Extractor:
    requestor: Trendyol_Requestor
    requestedNumber: int

    def __turnToDigit(self, num: str) -> float:
        s = ""
        for i in num:
            if i.isdigit() or i == ".":
                s += i

        return float(s)

    def __extract(self, product: BeautifulSoup, index: int) -> dict:
        result = {}
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

            details = self.requestor.get_product_details(result["link"])
            attrs = self.requestor.get_product_customizable_attrs(
                details["productGroupId"]
            )
            result["imageURL"] = details["smallImage"]
            self.__extract_sizes(resultSet=result, details=details)
            self.__extract_color_variants(resultSet=result, attrs=attrs)

        except Exception as e:
            print(f"Error in extracting product {index}")
            print(e)
            # print(product)

        return result

    def __extract_sizes(self, resultSet: dict, details: dict):
        sizes = details["allVariants"]
        if sizes:
            sizes = [
                {"size": variant["value"], "inStock": variant["inStock"]}
                for variant in sizes
            ]
            resultSet["sizes"] = sizes

    def __extract_color_variants(self, resultSet: dict, attrs: dict):
        if attrs:
            for attr in attrs:
                resultSet[attr["displayName"].lower()] = [
                    attribute["image"] for attribute in attr["attributes"]
                ]

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
                result = self.__extract(product, index)
                result["country"] = self.requestor.target_country
                resultSet.append(result)
                if len(resultSet) == self.requestedNumber:
                    break

        resultSet = resultSet[: self.requestedNumber]

        return resultSet
