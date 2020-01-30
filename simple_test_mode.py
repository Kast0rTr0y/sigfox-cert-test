from network import Sigfox
sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=Sigfox.RCZ1)
sigfox.test_mode(0,3)
