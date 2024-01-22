MACHINE_1 = True

BROKER_IP = '10.108.33.125'
SERVER_URL = 'http://10.108.33.110:8000'

if MACHINE_1:
    MACHINE_ID = "rpi1"
    TOKEN = "rpi1"
else:
    MACHINE_ID = "rpi2"
    TOKEN = "rpi2"
