# templatetags/custom_filters.py
from django import template

register = template.Library()


@register.filter
def attr(obj, attr_name):
    return getattr(obj, attr_name)

@register.filter
def get_model_fields(querySet):
    return querySet.model._meta.fields
