from django.db import models
from .sourceCountries import SourceCountries
from .targetCountries import TargetCountries


class Request(models.Model):
    search_word = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    avg_price = models.FloatField()
    target_country = models.CharField(max_length=255, choices=TargetCountries.choices)
    source_country = models.CharField(max_length=255, choices=SourceCountries.choices)
    requested_count = models.IntegerField(default=0, null=False, blank=False)
    price = models.FloatField()


class Result(models.Model):
    image_url = models.URLField()
    brand = models.CharField(max_length=100)
    product_name = models.CharField(max_length=255)
    original_price = models.FloatField(null=True, blank=True)
    discounted_price = models.FloatField(null=True, blank=True)
    currency = models.CharField(max_length=10)
    link = models.URLField()
    percentage = models.FloatField()
    request = models.ForeignKey(Request, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(original_price__isnull=False)
                | models.Q(discounted_price__isnull=False),
                name="both_original_and_discounted_price_not_null",
            )
        ]
