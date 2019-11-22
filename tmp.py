from network import Sigfox
import socket
import machine
import _thread
import time
import pycom

def sleep(sec):
    while (sec >= 0) :
        if sec > 10:
            sec -= 10
            print("X", end="")
            time.sleep(10)
        else:
            sec -= 1
            print(".", end="")
            time.sleep(1)


def siggi(a):
    sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ2)
    sigfox.public_key(True)
    s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
    s.setblocking(True)
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

    b = 0
    while True:
        print(time.time(), "send", b)
        start = time.time()
        s.send(bytes([6]))
        print(time.time(), "send", b, "completed in", time.time() - start, "s")
        pycom.rgbled(0x060202)
        b += 1


def blink(a):
    pycom.heartbeat(False)
    while True:
        #print(time.time(), "blink")
        print(".", end="")
        pycom.rgbled(0x000500)
        time.sleep_ms(600)
        #print(time.time(), "OFF")
        pycom.rgbled(0x000000)
        time.sleep_ms(400)


print("start multihreaded sigfox test (green blinking 1s, sending sigfox as fast as possible)")
pycom.heartbeat(False)
pycom.rgbled(0x100000)
time.sleep(1)
pycom.rgbled(0x001000)
time.sleep(1)
#time.sleep_ms(66)


_thread.start_new_thread(blink, (1,))
_thread.start_new_thread(siggi, (1,))


# pycom.rgbled(0x000010)
# time.sleep(10)
# machine.reset()
