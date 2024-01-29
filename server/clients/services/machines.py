from clients.models import Vmachine


class MachineService:
    @staticmethod
    def authenticate(token: str) -> Vmachine:
        machine = Vmachine.objects.get(token=token)
        return machine
