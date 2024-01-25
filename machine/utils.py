from enum import Enum


class Result(Enum):
    OK = 0
    NOT_ENOUGH_MONEY = 1
    NOT_ENOUGH_PRODUCTS = 2
    NOT_ACTIVE_CARD = 3
    UNKNOWN_PRODUCT = 4
    UNKNOWN_CARD = 5
    UNKNOWN_ERROR = 6