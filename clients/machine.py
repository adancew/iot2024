from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from clients.services import MachineService, StorageService, ProductService


@require_GET
def get_products_and_slots(request: HttpRequest):
    token = request.headers.get('Authorization').removeprefix('Bearer ')
    machine = MachineService.authenticate(token)
    if not machine:
        return HttpResponse(status=401)

    return JsonResponse({
        'products': ProductService.get_products(),
        'slots': StorageService.get_slots(machine.identifier)
    })
