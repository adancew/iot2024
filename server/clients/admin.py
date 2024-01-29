from django.contrib import admin
from django.contrib.admin.utils import unquote
from django.contrib.auth.admin import UserAdmin, sensitive_post_parameters_m
from django.core.exceptions import PermissionDenied

from .models import *

# Register your models here.
admin.site.register(Card)
admin.site.register(Transaction)
admin.site.register(Product)
admin.site.register(Slot)
admin.site.register(Vmachine)


admin.site.unregister(User)


@admin.register(User)
class AppUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not request.user.is_superuser:
            if 'is_superuser' in form.base_fields:
                form.base_fields['is_superuser'].disabled = True
            if 'user_permissions' in form.base_fields:
                form.base_fields['user_permissions'].disabled = True
            if obj is not None and obj.is_superuser:
                for field in ('username', 'password', 'first_name', 'last_name', 'email', 'is_staff', 'is_active',
                              'groups', 'user_permissions', 'last_login', 'date_joined'):

                    form.base_fields[field].disabled = True
                form.declared_fields['password'].help_text = ''
        return form

    @sensitive_post_parameters_m
    def user_change_password(self, request, id, form_url=""):
        obj = self.get_object(request, unquote(id))
        if not request.user.is_superuser and obj is not None and obj.is_superuser:
            raise PermissionDenied
        return super().user_change_password(request, id, form_url)
