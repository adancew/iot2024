from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Card)
admin.site.register(Transaction)
admin.site.register(Product)
admin.site.register(Slot)
admin.site.register(Vmachine)