from network import Sigfox
import pycom
import time
import ubinascii
import machine

def sleep(s):
    while s >= 0:
        time.sleep(1)
        print(".", end="")
        s -= 1
    print("")

def cw(f):
    s = 10.2
    pycom.rgbled(0x110000)
    print("NOISE (", s, ") ", end="")
    sigfox.cw( f, True)
    sleep(s)

    s = CS
    pycom.rgbled(0x001100)
    print("quiet (", s, ") ", end="")
    sigfox.cw( f, False)
    sleep(s)

pycom.heartbeat(False)
print("machine.unique_id:", ubinascii.hexlify( machine.unique_id() ))
print("machine.freq:", machine.freq() )
print("machine.info:")
machine.info()
print("pycom.wifi_on_boot:", pycom.wifi_on_boot())
print("pycom.wdt_on_boot:", pycom.wdt_on_boot())
# print("pycom.smart_config_on_boot:", pycom.smart_config_on_boot())

RCZ = Sigfox.RCZ3
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=RCZ )
print("sigfox version:", sigfox.version())
print("sigfox ID:", ubinascii.hexlify(sigfox.id()))
print("sigfox PAC:", ubinascii.hexlify(sigfox.pac()))
print("sigfox region:", RCZ)
print("sigfox frequencies:", sigfox.frequencies())
print("sigfox info:")
sigfox.info() # normally prints nothing, but patched FW prints private key
print("sigfox config:", sigfox.config()) # after reset RCZ3 defaults to (3, 5000, 0)
print("sigfox public key", sigfox.public_key())

CS = 10
f = sigfox.frequencies()[0]

print("continous", f, " Hz with carrier sense ", CS)
while True:
    cw(f)

pycom.heartbeat(True)
