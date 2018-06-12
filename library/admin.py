from django.contrib import admin

# Register your models here.
from .models import *


class LibraryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'codesearch')



admin.site.register(Card)
admin.site.register(Book)
admin.site.register(Library, LibraryAdmin)