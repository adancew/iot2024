import abc
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont
from config import *
import lib.oled.SSD1331 as SSD1331
import RPi.GPIO as GPIO 
import time

from mfrc522 import MFRC522

if TYPE_CHECKING:
    import storage
    import transactions

NUM_DISPLAY_PRODUCTS = 5
OLED_WIDTH = 96
OLED_HEIGHT  = 64

TEXT_HEIGHT = 12
DIM = 18

# init fonts
fontSmall = ImageFont.truetype('./lib/oled/Font.ttf', TEXT_HEIGHT)
disp = SSD1331.SSD1331()
wasButtonPressed = False
encoder_changed = False



# TODO: intergrate states with mqtt: BalanceRead, PurchaseRequest
# TODO: make products list cycilic (itertools cycle)

current_index=0


def encoderLeftFall(_):
    global encoder_right_value
    global encoder_changed
    encoder_right_value = GPIO.input(encoderRight)
    encoder_changed = True




class State(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def redButtonCallback() -> None:
        pass

    @abc.abstractmethod
    def greenButtonCallback() -> None:
        pass

    @abc.abstractmethod
    def displayMenu() -> None:
        pass

class Menu:
    def __init__(self, storage: 'storage.Storage',  transaction: 'transactions.TransactionManager') -> None:
        self._state = Initial(self)
        self._storage = storage 
        self.transactions = transaction

    @property
    def state(self) -> State:
        return self._state   

    def transitionTo(self, newState: State) -> None:
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
        #disp.clear()
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
        draw.text((0, TEXT_HEIGHT), "Green - Products", font=fontSmall)
        draw.text((0, TEXT_HEIGHT*2), "Red - Account Balance", font=fontSmall)
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
        draw.text((0, TEXT_HEIGHT*2), "to Card Reader", font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)

        card, _ = readCard()
        print(card)
        self._context.transactions.request_balance(card)

    def balance(self, balance: float):
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)
        draw.text((0, TEXT_HEIGHT), "Balance:", font=fontSmall)
        draw.text((0, TEXT_HEIGHT*2), str(round(balance, 2)), font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)
        




class ProductList(State):
    def __init__(self, context: Menu):
        self._context = context
        self.products = self._context._storage.products_list()

    def redButtonCallback(self) -> None:
        self._context.transitionTo(Initial(self._context))

    def greenButtonCallback(self) -> None:
        self._context.transactions.start_transaction(*(self.products[current_index][::-1]))
        self._context.transitionTo(PurchaseRequest(self._context))

    def move_up(self):
        global current_index
        current_index = min(current_index+1, len(self.products)-1)
    # current_index = max(0, current_index-1)

    def move_down(self):
        global current_index
        current_index = max(current_index-1, 0)


    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)

        start_index = current_index
        end_index = min(start_index+ NUM_DISPLAY_PRODUCTS,  len(self.products))

        for productIndex, displayListIndex in zip(range(start_index,end_index), range(NUM_DISPLAY_PRODUCTS)):

            product = self.products[productIndex][0]
            selected_indicator= "->" if productIndex==current_index else "  "

            draw.text((0,displayListIndex*TEXT_HEIGHT), 
                      f"{selected_indicator}{product.name}: {product.price}", 
                      font=fontSmall)
            
        disp.ShowImage(buffer_image, 0, 0)


class PurchaseRequest(State):
    def __init__(self, context: Menu):
        self._context = context

    def redButtonCallback(self) -> None:
        self._context.transitionTo(ProductList(self))

    def greenButtonCallback(self) -> None:
        pass

    def displayMenu(self) -> None:
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(buffer_image)
        draw.text((0, TEXT_HEIGHT), "Apply Card", font=fontSmall)
        draw.text((0, TEXT_HEIGHT*2), "to Card Reader", font=fontSmall)
        disp.ShowImage(buffer_image, 0, 0)

        card, _ = readCard()
        print(card)
        self._context.transactions.commit_transaction(card)

    def purchase(self, result):
        buffer_image = Image.new("RGB", (disp.width, disp.height), "BLACK")
        purchase_successful = result == 0

        draw = ImageDraw.Draw(buffer_image)
        if purchase_successful:
            draw.text((0, TEXT_HEIGHT), "You bought", font=fontSmall)
            draw.text((0, TEXT_HEIGHT*2), self.products[current_index], font=fontSmall)
        else:
            draw.text((0, TEXT_HEIGHT), "Your purchase", font=fontSmall)
            draw.text((0, TEXT_HEIGHT*2), "was unsuccessful", font=fontSmall)
        
        disp.ShowImage(buffer_image, 0, 0)

        # TODO possibly change the sleep
        time.sleep(3)

        # going back to products list
        self.redButtonCallback()


MIFAREReader = MFRC522()
def readCard():
        errs = 0
        while True:
            (status1, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
            if status1 == MIFAREReader.MI_OK:
                if errs >= 2:
                    (status2, uid) = MIFAREReader.MFRC522_Anticoll()
                    if status2 == MIFAREReader.MI_OK:
                        num = 0
                        for i in range(0, len(uid)):
                            num += uid[i] << (i*8)
                        return str(num), time.time()
                errs = 0
            else:
                errs += 1


def setup(menu: Menu):
    GPIO.add_event_detect(encoderLeft, GPIO.FALLING, callback=encoderLeftFall, bouncetime=20)
    GPIO.add_event_detect(buttonRed, GPIO.FALLING, callback=menu.redButtonCallback, bouncetime=200)
    GPIO.add_event_detect(buttonGreen, GPIO.FALLING, callback=menu.greenButtonCallback, bouncetime=200)
    disp.Init()
   
    disp.clear()


def loop(menu: Menu):
    global encoder_changed
    global wasButtonPressed

    if encoder_changed and type(menu.state) is ProductList:
            if encoder_right_value == GPIO.HIGH:
                menu.state.move_down()
            else:
                menu.state.move_up()
            encoder_changed = False
            menu.displayMenu()
        
    if wasButtonPressed:
        menu.displayMenu()
        wasButtonPressed = False

   
if __name__ == "__main__":
    menu = Menu()

    
    menu.displayMenu()


    
    
