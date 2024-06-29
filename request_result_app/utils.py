from rest_framework.response import Response
from rest_framework import status
from .sourceCountries import SourceCountries
from .targetCountries import TargetCountries
from ast import literal_eval
from django.db import models
import requests


class Utils:

    @staticmethod
    def check_needed_extraction_fields(data: dict):
        """Check if all needed fields are present in the data
        includes:
            searchWord:key word user is looking for
            sourceCountry:country where the search is being made
            targetCountry:country where the search will be made in trendyol
        """
        needed_fields = ["searchWord", "sourceCountry", "targetCountry"]
        for field in needed_fields:
            if field not in data:
                return Response(
                    {"message": f"{field} is missing in the request"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return True

    @staticmethod
    def check_source_target_country(source_country: str, target_country: str):
        """Check if source and target country are in the available countries"""
        if not hasattr(SourceCountries, source_country.upper()):
            return Response(
                {"message": f"{source_country} is not a valid source country"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not hasattr(TargetCountries, target_country.upper()):
            return Response(
                {"message": f"{target_country} is not a valid target country"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return True

    @staticmethod
    def get_country_from_choices(country: str, choices: models.TextChoices) -> dict:
        """Get country details from the choices.Choices has to be an instance of django.db.models.TextChoices"""
        return literal_eval(getattr(choices, country.upper()))

    @staticmethod
    def calculate_avg_price(results: list) -> float:
        """Calculate the average price of the prices
        prioritizing discounted price if available
        """
        try:
            return sum(
                [
                    (
                        result["discountedPrice"]
                        if "discountedPrice" in result
                        else result["originalPrice"]
                    )
                    for result in results
                ]
            ) / len(results)
        except:
            return 0

    @staticmethod
    def get_rate(sourceCountry: dict, targetCountry: dict):
        # https://cdn.jsdelivr.net/npm/@fawazahmed0/currency-api@latest/v1/currencies/eur.json
        url = f"https://api.exchangerate-api.com/v4/latest/{targetCountry['currency']}"
        response = requests.get(url)
        data = response.json()
        return data["rates"][sourceCountry["currency"].upper()]

    @staticmethod
    def convert_prices(sourceCountry: dict, targetCountry: dict, results: list):
        rate = Utils.get_rate(sourceCountry, targetCountry)
        for result in results:
            if "originalPrice" in result:
                result["originalPrice"] = round(result["originalPrice"] * rate, 2)
            if "discountedPrice" in result:
                result["discountedPrice"] = round(result["discountedPrice"] * rate, 2)
        return results

    @staticmethod
    def check_is_digit(data: str):
        try:
            float(data)
            return True
        except:
            return False

    @staticmethod
    def set_profit_change(results, price):
        for result in results:
            result["percentage"] = round(
                (
                    (
                        price
                        - (
                            result["discountedPrice"]
                            if "discountedPrice" in result
                            else result["originalPrice"]
                        )
                    )
                    / price
                )
                * 100,
                2,
            )
            result["profit/loss"] = round(
                price
                - (
                    result["discountedPrice"]
                    if "discountedPrice" in result
                    else result["originalPrice"]
                ),
                2,
            )
        return results
