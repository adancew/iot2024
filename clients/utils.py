from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import ObjectDoesNotExist


def is_owner(user):
    #return user.groups.filter(name='Owners').exists()
    return user.is_staff
