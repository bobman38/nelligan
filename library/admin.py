from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Card)
admin.site.register(Book)
