from rest_framework.serializers import ModelSerializer
from .models import Request, Result


class RequestSerializer(ModelSerializer):
    class Meta:
        model = Request
        fields = "__all__"


class ResultSerializer(ModelSerializer):
    class Meta:
        model = Result
        fields = "__all__"
