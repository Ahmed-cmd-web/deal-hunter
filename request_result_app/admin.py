from django.contrib import admin
from .models import Request, Result


admin.site.register([Request, Result])
