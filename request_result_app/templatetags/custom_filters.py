# templatetags/custom_filters.py
from django import template
import json
register = template.Library()


@register.filter
def attr(obj, attr_name):
    if attr_name=='SIZES' and obj[attr_name] != 'N/A':
        return [size['size'] for size in obj[attr_name] if size['inStock']]
    return obj[attr_name]

@register.filter
def get_model_fields(querySet):
    if not len(querySet):
        return []
    return querySet[0].keys()


@register.filter
def get_keys(_,item):
    return item.keys()
