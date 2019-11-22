from network import Sigfox
import utime
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
print(sigfox.frequencies())
sigfox.cw( sigfox.frequencies()[0], True)
utime.sleep(10)
sigfox.cw( sigfox.frequencies()[0], False)
