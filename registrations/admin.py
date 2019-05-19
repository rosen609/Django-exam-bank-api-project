from django.contrib import admin

from .models import *

admin.site.register(Person)
admin.site.register(Accountant)
admin.site.register(Manager)
admin.site.register(Customer)
admin.site.register(Currency)
admin.site.register(AccountProduct)
admin.site.register(Account)
