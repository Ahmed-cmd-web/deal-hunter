from django.contrib import admin
from .models import Request, Result
from django.utils.html import format_html
import json



class RequestAdmin(admin.ModelAdmin):
    all_fields = (
        [field.name for field in Request._meta.fields] if Request != None else []
    )
    list_display: list = [
        field
        for field in all_fields
        if field not in ["source_country", "target_country"]
    ] + ["export_to", "import_from"]
    # list_filter: list = all_fields
    search_fields: list = all_fields

    def export_to(self, obj):
        return obj.source_country

    def import_from(self, obj):
        return obj.target_country


class ResultAdmin(admin.ModelAdmin):
    all_fields = [field.name for field in Result._meta.fields] if Result != None else []
    list_display = [
        "id",
        "image_tag",
        "brand",
        "product_name",
        "original_price",
        "discounted_price",
        "currency",
        # "percentage",
        # "archived",
        "sizes_dropdown",
        "colors",
        "import_from",
        "search_word" ,
        "product_link",
    ]
    # list_filter: list = all_fields
    search_fields: list = [field for field in all_fields if field != "request"]

    def import_from(self, obj):
        return obj.country

    def sizes_dropdown(self, obj):
        if obj.sizes != "N/A":
            sizes = json.loads(obj.sizes) if isinstance(obj.sizes, str) else obj.sizes
            result = "\n".join(
                [
                    f'<option {"" if size["inStock"] else "disabled"}>{size["size"]}</option>'
                    for size in sizes
                ]
            )
            return format_html(f"<select>{result}</select>")
        return "N/A"

    def pretty_colors(self, obj):
        if obj.colors != "N/A":
            result = "\n".join(
                [f'<span>{color["color"]}</span>' for color in obj.colors]
            )
            return format_html(result)

    def product_link(self, obj):
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank">{}</a>', obj.link, "View Product"
            )
        return "No URL"

    def image_tag(self, obj):
        if obj.image_url:
            return format_html(
                f'<img src="{obj.image_url}" style="width: 45px; height:45px;" />'
            )
        return "No Image"


admin.site.register(Request, RequestAdmin)
admin.site.register(Result, ResultAdmin)
