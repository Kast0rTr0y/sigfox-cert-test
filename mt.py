from network import Sigfox
import socket
import machine
import _thread
import time
import pycom
import sys

wait = 24 # how many seconds do we need to wait after every second frame (starting after the first) in RCZ2 and 4
last = -wait # when was the last sigfox message sent

print(wait)

def siggi(a):
    global last
    global wait
    b = 0
    while True:
        d = b % 256
        # if b % 2 == 0:
        #     print(time.time(), "odd message .. check the delay")
        delay = time.time() - last
        if delay < wait:
            print(time.time(), "sleep", wait-delay)
            time.sleep(wait-delay)
        print(time.time(), "send", b, d)
        start = time.time()
        s.send(bytes([d]))
        end = time.time()
        print(time.time(), "send", b, d, "completed in (", end, "-", start, ") = ", end - start, "s")
        last = start
        pycom.rgbled(0x060202)
        b += 1

def blink(a):
    pycom.heartbeat(False)
    c = 0
    while True:
        #print(time.time(), "blink")
        print(".", end="")
        pycom.rgbled(0x000500)
        time.sleep_ms(700)
        #print(time.time(), "OFF")
        pycom.rgbled(0x000000)
        time.sleep_ms(300)
        c += 1
        if c == 10:
            # a newline every tenth second
            print("")
            c = 0

print("start multihreaded sigfox test (green blinking 1s, sending sigfox as fast as possible)")
pycom.heartbeat(False)
pycom.rgbled(0x100000)

sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ2 )
sigfox.public_key(True)
s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
s.setblocking(True)
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

time.sleep(1)
pycom.rgbled(0x001000)
time.sleep(1)

_thread.start_new_thread(blink, (1,))
_thread.start_new_thread(siggi, (1,))
while True:
    time.sleep(5)
    pycom.rgbled(0x000022)