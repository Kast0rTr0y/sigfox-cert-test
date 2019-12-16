from network import LoRa
import socket
import machine
import time
# initialise LoRa in LORA mode
# Please pick the region that matches where you are using the device:
# Asia = LoRa.AS923
# Australia = LoRa.AU915
# Europe = LoRa.EU868
# United States = LoRa.US915
# more params can also be given, like frequency, tx power and spreading factor
lora = LoRa(mode=LoRa.LORA, region=LoRa.EU868, tx_power = 20)
# create a raw LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
while True:
    # send some data
    s.setblocking(True)
    s.send('Hello')
    #s.setblocking(False)
    #data = s.recv(64)
