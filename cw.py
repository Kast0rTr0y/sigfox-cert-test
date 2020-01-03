from network import Sigfox
import pycom
import utime

def cw(f):
    print("continous", f, " Hz for", s, "seconds")
    pycom.rgbled(0x001100)
    sigfox.cw( f, True)
    utime.sleep(s)
    sigfox.cw( f, False)

pycom.heartbeat(False)
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ3 )
print(sigfox.frequencies())
s = 10

cw(sigfox.frequencies()[0])
# cw(sigfox.frequencies()[1])

pycom.heartbeat(True)
