import datetime as dt

from ..models import Transaction, Card, Product


class LoggingService:
    @staticmethod
    def log_transaction(card: Card, product: Product, machine_id: str, timestamp: int):
        time = dt.datetime.fromtimestamp(timestamp, dt.timezone.utc)
        Transaction.objects.create(user_fk=card.user_fk, vmachine_fk_id=machine_id, product_fk=product,
                                   price=product.price, transaction_time=time)
