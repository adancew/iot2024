import requests

from configuration import SERVER_URL, TOKEN
from mqtt import start_mqtt
from storage import Storage
from transactions import TransactionManager
from gui import Menu, setup, loop


def main():
    storage = Storage()
    transactions = TransactionManager(storage)
    mqtt = start_mqtt(storage, transactions)
    menu = Menu(storage, transactions)
    transactions.mqtt = mqtt
    
    transactions.menu = menu
    r = requests.get(f'{SERVER_URL}/machine/initial/', headers={
        'Authorization': 'Bearer ' + TOKEN
    })
    if r.status_code == 200:
        storage.initialize(r.json())
    else:
        print('Failed to initialize storage')
        return
    print('Storage initialized')

    setup(menu)

    menu.displayMenu()

    while True:
        loop(menu)


if __name__ == '__main__':
    main()
