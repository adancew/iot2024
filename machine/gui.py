import abc
from typing import TYPE_CHECKING
import time

from PIL import Image, ImageDraw, ImageFont

from configuration import DEPLOY
from utils import Result

if DEPLOY:
    from mfrc522 import MFRC522

    from config import *
    import lib.oled.SSD1331 as SSD1331
    import RPi.GPIO as GPIO
else:
    import keyboard  # pip install keyboard
    from test import DisplayMock

if TYPE_CHECKING:
    import storage
    import transactions

NUM_DISPLAY_PRODUCTS = 6
OLED_WIDTH = 96
OLED_HEIGHT = 64

TEXT_HEIGHT = 10
DIM = 18

# init fonts
fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', TEXT_HEIGHT)

if DEPLOY:
    disp = SSD1331.SSD1331()
    RIGHT = GPIO.HIGH
else:
    disp = DisplayMock()
    RIGHT = False

wasButtonPressed = False
state_changed = False
encoder_changed = False
encoder_right_value = False

# TODO: intergrate states with mqtt: BalanceRead, PurchaseRequest
# TODO: make products list cycilic (itertools cycle)

current_index = 0


def encoderLeftFall(event):
    global encoder_right_value
    global encoder_changed
    if DEPLOY:
        encoder_right_value = GPIO.input(encoderRight)
    else:
        encoder_right_value = event['right']
    encoder_changed = True


class State(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def redButtonCallback(self) -> None:
        pass

    @abc.abstractmethod
    def greenButtonCallback(self) -> None:
        pass

    @abc.abstractmethod
    def displayMenu(self) -> None:
        pass


class Menu:
    def __init__(self, storage: 'storage.Storage', transaction: 'transactions.TransactionManager') -> None:
        self._state = Initial(self)
        self.storage = storage
        self.transactions = transaction

    @property
    def state(self) -> State:
        return self._state

    def transitionTo(self, newState: State) -> None:
        global state_changed
        state_changed = True
        self._state = newState

    def greenButtonCallback(self, _) -> None:
        global wasButtonPressed
        wasButtonPressed = True
        self._state.greenButtonCallback()

    def redButtonCallback(self, _) -> None:
        global wasButtonPressed
        wasButtonPressed = True
        self._state.redButtonCallback()

    def displayMenu(self) -> None:
        self._state.displayMenu()


# states of the menu
class Initial(State):

    def __init__(self, context: Menu):
        self._context = context

    def redButtonCallback(self) -> None:
        self._context.transitionTo(BalanceRead(self._context))

    def greenButtonCallback(self) -> None:
        self._context.transitionTo(ProductList(self._context))

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")

        draw = ImageDraw.Draw(buffer_image)
        draw.text((0, TEXT_HEIGHT), "Green button:", font=fontSmall,  fill="green")
        draw.text((0, TEXT_HEIGHT*2), "Products", font=fontSmall)
        draw.text((0, TEXT_HEIGHT*3), "", font=fontSmall)
        draw.text((0, TEXT_HEIGHT*4), "Red button:", font=fontSmall,  fill="red")
        draw.text((0, TEXT_HEIGHT*5), "Account Balance", font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)


class BalanceRead(State):
    def __init__(self, context: Menu):
        self._context = context

    def redButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def greenButtonCallback(self) -> None:
        pass

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")

        draw = ImageDraw.Draw(buffer_image)
        draw.text((0, TEXT_HEIGHT), "Apply Card", font=fontSmall)
        draw.text((0, TEXT_HEIGHT * 2), "to Card Reader", font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)

        card, t = readCard()
        if card is not None:
            self._context.transactions.request_balance(card, t)

    def balance(self, balance: float, result: Result):
        self._context.transitionTo(BalanceResult(self._context, balance, result))


class BalanceResult(State):
    def __init__(self, context: Menu, balance: float, result: Result):
        self._context = context
        self._balance = balance
        self._result = result

    def redButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def greenButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))


    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)
        # TODO: Add option of unsuccessful read
        draw.text((0, TEXT_HEIGHT), "Balance:", font=fontSmall)
        draw.text((0, TEXT_HEIGHT * 2), str(round(self._balance, 2)), font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)


class ProductList(State):
    def __init__(self, context: Menu):
        self._context = context
        self.products = self._context.storage.products_list()

    def redButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def greenButtonCallback(self) -> None:
        self._context.transactions.start_transaction(*(self.products[current_index][::-1]))
        self._context.transitionTo(PurchaseRequest(self._context))

    def move_up(self):
        global current_index
        current_index = min(current_index + 1, len(self.products) - 1)

    # current_index = max(0, current_index-1)

    def move_down(self):
        global current_index
        current_index = max(current_index - 1, 0)

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)

        start_index = current_index
        end_index = min(start_index + NUM_DISPLAY_PRODUCTS, len(self.products))

        for productIndex, displayListIndex in zip(range(start_index, end_index), range(NUM_DISPLAY_PRODUCTS)):
            product = self.products[productIndex][0]
            selected_indicator = "->" if productIndex == current_index else "  "

            draw.text((0, displayListIndex * TEXT_HEIGHT),
                      f"{selected_indicator}{product.name}: {product.price}",
                      font=fontSmall)

        disp.ShowImage(buffer_image, 0, 0)


class PurchaseRequest(State):
    def __init__(self, context: Menu):
        self._context = context

    def redButtonCallback(self) -> None:
        self._context.transitionTo(ProductList(self._context))

    def greenButtonCallback(self) -> None:
        pass

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)
        draw.text((0, TEXT_HEIGHT), "Apply Card", font=fontSmall)
        draw.text((0, TEXT_HEIGHT * 2), "to Card Reader", font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)

        card, t = readCard()
        if card is not None:
            self._context.transactions.commit_transaction(card, t)

    def purchase(self, result, product_name):
        self._context.transitionTo(PurchaseResult(self._context, product_name, result))


class PurchaseResult(State):
    def __init__(self, context: Menu, product_name: str, result: Result):
        self._context = context
        self._product_name = product_name
        self._result = result

    def redButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def greenButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        purchase_successful = self._result == Result.OK

        draw = ImageDraw.Draw(buffer_image)
        if purchase_successful:
            draw.text((0, TEXT_HEIGHT), "You bought", font=fontSmall)
            draw.text((0, TEXT_HEIGHT * 2), self._product_name, font=fontSmall)
        else:
            draw.text((0, TEXT_HEIGHT), "Your purchase", font=fontSmall)
            draw.text((0, TEXT_HEIGHT * 2), "was unsuccessful", font=fontSmall)

        disp.ShowImage(buffer_image, 0, 0)


if DEPLOY:
    MIFAREReader = MFRC522()


def readCard():
    if not DEPLOY:
        return '782264110091', int(time.time())
    errs = 0
    while not state_changed:
        (status1, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
        if status1 == MIFAREReader.MI_OK:
            if errs >= 2:
                (status2, uid) = MIFAREReader.MFRC522_Anticoll()
                if status2 == MIFAREReader.MI_OK:
                    num = 0
                    for i in range(0, len(uid)):
                        num += uid[i] << (i * 8)
                    return str(num), int(time.time())
            errs = 0
        else:
            errs += 1
    return None, None


def setup(menu: Menu):
    if DEPLOY:
        GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encoderLeftFall, bouncetime=20)
        GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=menu.redButtonCallback, bouncetime=200)
        GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=menu.greenButtonCallback, bouncetime=200)
    else:
        keyboard.add_hotkey('left', encoderLeftFall, args=({'right': False},))
        keyboard.add_hotkey('right', encoderLeftFall, args=({'right': True},))
        keyboard.add_hotkey('r', menu.redButtonCallback, args=(None,))
        keyboard.add_hotkey('g', menu.greenButtonCallback, args=(None,))
    disp.Init()

    disp.clear()


def loop(menu: Menu):
    global encoder_changed
    global wasButtonPressed
    global state_changed

    if encoder_changed and isinstance(menu.state, ProductList):
        if encoder_right_value == RIGHT:
            menu.state.move_down()
        else:
            menu.state.move_up()
        encoder_changed = False
        menu.displayMenu()

    if wasButtonPressed or state_changed:
        wasButtonPressed = False
        state_changed = False
        menu.displayMenu()
