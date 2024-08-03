from rest_framework.serializers import ModelSerializer
from .models import Request, Result
import json


class ModifiedModelSerializer(ModelSerializer):
    def to_representation(self, instance):
        result = super().to_representation(instance)
        res = {}
        for key in result:
            newKey = " ".join(word.upper() for word in key.split("_"))
            res[newKey] = result[key]
        if "REQUEST" in res and res.get("REQUEST") == None:
            res.pop("REQUEST")
        if (
            "COLORS" in res
            and res.get("COLORS") != "N/A"
            and isinstance(res["COLORS"], str)
        ):
            res["COLORS"] = json.loads(res["COLORS"])
        if (
            "SIZES" in res
            and res.get("SIZES") != "N/A"
            and isinstance(res["SIZES"], str)
        ):
            res["SIZES"] = json.loads(res["SIZES"])
        if (
            "CREATED AT" in res
            and res.get("CREATED AT") != None
            and isinstance(res["CREATED AT"], str)
        ):
            res["CREATED AT"] += " UTC"
        return res


class RequestSerializer(ModifiedModelSerializer):
    class Meta:
        model = Request
        fields = "__all__"


class ResultSerializer(ModifiedModelSerializer):
    class Meta:
        model = Result
        exclude = ["archived", "percentage"]
