from django.contrib import admin

from .models import *

admin.site.register(Person)
admin.site.register(Company)
admin.site.register(Accountant)
admin.site.register(Manager)