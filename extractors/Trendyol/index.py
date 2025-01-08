from dataclasses import dataclass
from requestors.trendyol.index import Trendyol_Requestor
from bs4 import BeautifulSoup


@dataclass
class Trendyol_Extractor:
    requestor: Trendyol_Requestor
    requestedNumber: int

    def __turnToDigit(self, num: str) -> float:
        from price_parser import Price
        return Price.fromstring(num).amount_float
       

    def __extract(self, product: BeautifulSoup,details, index: int) -> dict:
        result = {}
        try:
            result["imageURL"] = product.find("img").get("src")
            result["brand"] = product.find("span", class_="product-brand").getText()
            result["productName"] = product.find(
                "span", class_="product-name-text"
            ).getText()


            suspectable_prices_area_elements_classes=['rrp-location-right','promotion-price-wrapper','p-price-wrapper']
            pricesArea = None
            for suspectable_class in suspectable_prices_area_elements_classes:
                pricesArea = product.find("div", class_=suspectable_class)
                if pricesArea != None:
                    break
            
            if pricesArea == None:
                result["discountedPrice"] = product.find(
                    "span", class_="discounted-price"
                ).getText()
                result["currency"] = product.find("span", class_="currency").getText()
            
            elif pricesArea.find('div',class_='p-strikethrough-price') != None:
                result["originalPrice"] = pricesArea.find('div',class_='p-strikethrough-price').getText()
                discount_area = pricesArea.find('div',class_='p-sale-price-wrapper')
                if discount_area != None:
                    result["discountedPrice"] = discount_area.find('span',class_='integer-part').getText() + discount_area.find('span',class_='decimal-part').getText()
                result["currency"] = discount_area.find('div',class_='p-currency').getText()
            
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
                originalPriceElem=product.find("p", class_="selling-price")
                if originalPriceElem == None:
                    originalPriceElem = pricesArea.find("div", class_="p-sale-price")
                    result['originalPrice'] = originalPriceElem.find('span',class_='integer-part').getText() + originalPriceElem.find('span',class_='decimal-part').getText()
                    result['currency'] = pricesArea.find('div',class_='p-currency').getText()
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
            # details = self.requestor.get_product_details(result["link"])
            # attrs = self.requestor.get_product_customizable_attrs(
            #     details["productGroupId"]
            # )
            result["imageURL"] = details["smallImage"]
            self.__extract_sizes(resultSet=result, details=details)
            # self.__extract_color_variants(resultSet=result, attrs=attrs)
        except Exception as e:
            print(f"Error in extracting product {index}")
            # print(e.args)
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
            if (bs.find('div',class_='no-result-suggestions-wrapper') or bs.find('div',class_='no-result')):
                break
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
    

    async def extract_requested_products_async(self):
        resultSet = []
        i = 1
        NUMBER_OF_PRODUCTS_PER_PAGE=20
        pages=await self.requestor.extract_pages_async([i for i in range(1,max(self.requestedNumber,10)//NUMBER_OF_PRODUCTS_PER_PAGE)])
        print('pages_extracted')
        if not len(pages):
            print(pages)
        links=[]
        for page_products in pages:
            bs = BeautifulSoup(page_products, "html.parser")
            if (bs.find('div',class_='no-result-suggestions-wrapper') or bs.find('div',class_='no-result')):
                break
            page_products = bs.find_all(
                class_="product", attrs={"data-testid": "product-card"}
            )
            if not page_products:
                break
            i += 1
            
            for index, product in enumerate(page_products):
                links.append(f'https://trendyol.com{product.find("a").get("href")}')
        if not len(links):
            print(links)
        products_details=await self.requestor.aget_products_details(links)
        print('details extracted')

        for page_products in pages:
            bs = BeautifulSoup(page_products, "html.parser")
            if (bs.find('div',class_='no-result-suggestions-wrapper') or bs.find('div',class_='no-result')):
                break
            page_products = bs.find_all(
                class_="product", attrs={"data-testid": "product-card"}
            )
            if not page_products:
                break
            i += 1
            
            for index, product in enumerate(page_products):
                result = self.__extract(product,products_details[index], index)
                result["country"] = self.requestor.target_country
                resultSet.append(result)
                if len(resultSet) == self.requestedNumber:
                    break
        print('done')
        print(len(resultSet))
        resultSet = resultSet[: self.requestedNumber]

        return resultSet
    


