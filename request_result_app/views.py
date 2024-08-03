from rest_framework.viewsets import ModelViewSet
from .models import Request, Result
from .serializers import RequestSerializer, ResultSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from .utils import Utils
from .targetCountries import TargetCountries
from .sourceCountries import SourceCountries
from requestors.trendyol.index import Trendyol_Requestor
from extractors.Trendyol.index import Trendyol_Extractor
from ast import literal_eval
from operator import itemgetter
from django.shortcuts import render
import os
import json


class RequestViewSet(ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer

    @action(detail=False, methods=["get"], url_path="oldRequests")
    def render_old_requests(self, request):
        return render(
            request,
            "oldRequestsResults.html",
            context={
                "development": os.getenv("DEVELOPMENT_MODE", "False") == "True",
                "querySet": RequestSerializer(Request.objects.all(), many=True).data,
                "title": "Old Requests List",
            },
        )

    @action(detail=False, methods=["get"])
    def get_countries(self, _):
        return Response(
            {
                "target": [literal_eval(country) for country in TargetCountries.values],
                "source": [literal_eval(country) for country in SourceCountries.values],
            },
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def get_count(self, request):
        validation = Utils.check_needed_extraction_fields(request.data)
        if validation is not True:
            return validation
        validation = Utils.check_source_target_country(
            request.data["sourceCountry"], request.data["targetCountry"]
        )
        if validation is not True:
            return validation

        target_country_data = Utils.get_country_from_choices(
            request.data["targetCountry"], TargetCountries
        )
        requestor = Trendyol_Requestor(
            target_country_data["name"], request.data["searchWord"]
        )
        return Response(
            {"count": int(requestor.getItemsCount())}, status=status.HTTP_200_OK
        )

    @action(detail=False, methods=["post"])
    def extract_trendyol_results(self, request):
        if not (count := request.data.get("count")) or (
            type(count) == str and not count.isdigit()
        ):
            return Response(
                {"message": "Please provide a valid count"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        count = int(count)
        if not (price := request.data.get("price")) or (
            type(price) == str and not Utils.check_is_digit(price)
        ):
            return Response(
                {"message": "Please provide a valid price"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        price = float(price)
        validation = Utils.check_needed_extraction_fields(request.data)
        if validation is not True:
            return validation
        validation = Utils.check_source_target_country(
            request.data["sourceCountry"], request.data["targetCountry"]
        )
        if validation is not True:
            return validation

        target_country_data = Utils.get_country_from_choices(
            request.data["targetCountry"], TargetCountries
        )
        source_country_data = Utils.get_country_from_choices(
            request.data["sourceCountry"], SourceCountries
        )
        requestor = Trendyol_Requestor(
            target_country_data["name"], request.data["searchWord"]
        )
        extractor = Trendyol_Extractor(requestor, count)
        results = extractor.extract_requested_products()
        Utils.convert_prices(source_country_data, target_country_data, results)
        Utils.set_profit_change(results, price)

        return Response(
            {"results": sorted(results, key=itemgetter("profit/loss"), reverse=True)},
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=["post"])
    def save_request(self, request):
        needed_req_fields = [
            "searchWord",
            "count",
            "price",
            "results",
            "sourceCountry",
            "targetCountry",
        ]

        for field in needed_req_fields:
            if field not in request.data:
                return Response(
                    {"message": f"Please provide the {field} field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        validation = Utils.check_source_target_country(
            request.data["sourceCountry"], request.data["targetCountry"]
        )
        if validation is not True:
            return validation

        target_country_data = Utils.get_country_from_choices(
            request.data["targetCountry"], TargetCountries
        )
        source_country_data = Utils.get_country_from_choices(
            request.data["sourceCountry"], SourceCountries
        )
        results =json.loads(request.data["results"])
        avg = Utils.calculate_avg_price(results=results)
        created_request = Request.objects.create(
            search_word=request.data["searchWord"],
            target_country=target_country_data["name"],
            source_country=source_country_data["name"],
            requested_count=request.data["count"],
            price=request.data["price"],
            avg_price=avg,
            found_count=len(results),
        )

        results_objects = []
        for result in results:
            results_objects.append(
                Result(
                    image_url=result["imageURL"],
                    brand=result["brand"],
                    product_name=result["productName"],
                    original_price=result.get("originalPrice"),
                    discounted_price=result.get("discountedPrice"),
                    currency=result["currency"],
                    link=result["link"],
                    sizes=result.get("sizes", "N/A"),
                    colors=result.get("colors", "N/A"),
                    country=result["country"],
                    request=created_request,
                    archived=False,
                )
            )
        Result.objects.bulk_create(results_objects)

        return Response(
            {"message": "Request saved successfully", "id": created_request.id},
            status=status.HTTP_201_CREATED,
        )


class ResultViewSet(ModelViewSet):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer

    @action(detail=True, methods=["get"], url_path="oldResults")
    def render_old_request_results(self, request, pk=None):
        querySet = Result.objects.filter(request_id=pk)

        return render(
            request,
            "oldRequestsResults.html",
            context={
                "development": os.getenv("DEVELOPMENT_MODE", "False") == "True",
                "querySet": ResultSerializer(querySet, many=True).data,
                "title": "Old Results List",
            },
        )

    @action(detail=False, methods=["post"])
    def save_deal(self, request):
        # check if all fields needed to create a result are provided
        needed_fields = [
            "imageURL",
            "brand",
            "productName",
            "currency",
            "link",
            "country",
        ]

        for field in needed_fields:
            if field not in request.data:
                return Response(
                    {"message": f"Please provide the {field} field"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        if (
            "originalPrice" not in request.data
            and "discountedPrice" not in request.data
        ):
            return Response(
                {"message": "Please provide either originalPrice or discountedPrice"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = Result.objects.create(
            image_url=request.data["imageURL"],
            brand=request.data["brand"],
            product_name=request.data["productName"],
            original_price=request.data.get("originalPrice"),
            discounted_price=request.data.get("discountedPrice"),
            currency=request.data["currency"],
            link=request.data["link"],
            sizes=request.data.get("sizes", "N/A"),
            colors=request.data.get("colors", "N/A"),
            country=request.data["country"],
            archived=True,
        )

        return Response(
            {"message": "Deal saved successfully", "id": result.id},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["get"])
    def saved_deals(self, request):
        return render(
            request,
            "oldRequestsResults.html",
            context={
                "development": os.getenv("DEVELOPMENT_MODE", "False") == "True",
                "querySet": ResultSerializer(
                    Result.objects.filter(archived=True), many=True
                ).data,
                "title": "Saved Deals List",
            },
        )
