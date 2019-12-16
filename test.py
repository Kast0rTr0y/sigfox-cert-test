from network import Sigfox
from network import WLAN
from network import Server
import socket
import utime
import ubinascii
import pycom
import machine

##############################################################
## select the test you want to run by (un)commenting

## for use with Sigfox Radio Signal Analyzer
## Uplink
# test = "UL - RF" # ManualVerdict
# test = "UL - Protocol" # [2 minutes]
# test = "UL - Non Volatile Memory" # ManualVerdict
# test = "UL - Public Key"
# test = "UL - Frequency Distribution" # [20-30 minutes] (start 11:26) with config 14 and reset until tests 11+12 are complete (config 34 running until the end is more than 1h)
test = "UL - Frequency Synthesis"  ## [<= 2 minutes]
## Downlink:
test = "DL - Downlink" # Use for any of "DL-Protocol", "DL-Start of Listening" and "DL-End of Listening"
test = "DL - Link Budget" # DL-Link Budget [439s couple minutes, then test is complete and you can reset the DUT]
# test = "DL - GFSK Receiver" # Test Mode TX-BPSK has to be executed just before this test.

## for use with Sigfox Network Emulator
# test = "MyTest"
# test = "MyDownlink"
# test = "None"



##############################################################
# ## select the region
RCZ = Sigfox.RCZ2


# RCZ1
#   Europe, Oman & South Africa.
#   UL= 868130000 Hz
#   DL= 869525000 Hz
# RCZ2
#   USA, Mexico & Brazil.
#   UL= 902200000 Hz
#   DL= 905200000 Hz
# RCZ3
#   Japan.
# RCZ4
#   Australia, New Zealand, Singapore, Taiwan, Hong Kong, Colombia & Argentina.

# test mode constants for sigfox api
SFX_TEST_MODE_TX_BPSK     = 0
SFX_TEST_MODE_TX_PROTOCOL = 1
SFX_TEST_MODE_RX_PROTOCOL = 2
SFX_TEST_MODE_RX_GFSK     = 3
SFX_TEST_MODE_RX_SENSI    = 4
SFX_TEST_MODE_TX_SYNTH    = 5


# WLAN().deinit()
# Server().deinit()
#### changing the following needs a reset of the device to take effect!
# pybytes.smart_config(False)
# pybytes.set_config("pybytes_autostart","true")
# pycom.wifi_on_boot(False)
# pycom.wdt_on_boot(False)


print("machine.unique_id:", ubinascii.hexlify( machine.unique_id() ))
print("machine.freq:", machine.freq() )
print("machine.info:")
machine.info()

print("pycom.wifi_on_boot:", pycom.wifi_on_boot())
print("pycom.wdt_on_boot:", pycom.wdt_on_boot())
# print("pycom.smart_config_on_boot:", pycom.smart_config_on_boot())


sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=RCZ)
print("sigfox version:", sigfox.version())
print("sigfox ID:", ubinascii.hexlify(sigfox.id()))
print("sigfox PAC:", ubinascii.hexlify(sigfox.pac()))
print("sigfox region:", RCZ)
print("sigfox frequencies:", sigfox.frequencies())
print("sigfox info:")
sigfox.info() # normally prints nothing, but I hacked it to print private key

#sigfox.public_key(True)
print("sigfox public key", sigfox.public_key())

s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
s.setblocking(True)
if ( test == "MyDownlink" ):
    # configure socket as uplink + downlink
    print("socket:", "up and down")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)
else:
    # configure socket as uplink only
    print("socket:", "uplink only")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

print("test:", test)
################################################################################






wait = 24 # how many seconds do we need to wait after every second frame (starting after the first) in RCZ2 and 4
last = -wait # when was the last sigfox message sent

def sleep(s):
    print("sleep", s, end="")
    while s:
        utime.sleep(1)
        s -= 1
        print(".", end="")
    print("")


def send(msg):
    global last
    global wait
    global s
    # if RCZ == Sigfox.RCZ2 or RCZ == Sigfox.RCZ4:
    #     delay = utime.time() - last
    #     if delay < wait:
    #         sleep(wait-delay)
    # else:
    sleep(1)
    print("send", ubinascii.hexlify(msg))
    last = utime.time()
    r = s.send(msg)
    return r











################################################################################
# run test
start = utime.time()
# pycom.heartbeat(False)
# pycom.rgbled(0x000300)
if test == "UL - RF":
    for x in range(0,2):
        sigfox.test_mode( SFX_TEST_MODE_TX_BPSK, 3)
        sleep(5)
elif test == "UL - Protocol":
    # send a single bit: 0
    print("send False")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, False)
    s.send('')
    sleep(1)

    # send a single bit: 1
    print("send True")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, True)
    s.send('')
    sleep(1)

    # send an out of bound msg
    print("send OOB")
    # use the socket to send a Sigfox Out Of Band message
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, True)
    s.send('')
    sleep(1)
    # disable Out-Of-Band to use the socket normally
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, False)

    send(bytes([0x40]))
    send(bytes([0x40, 0x41]))
    send(bytes([0x40, 0x41, 0x42]))
    send(bytes([0x40, 0x41, 0x42, 0x43]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A ]))
    send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B ]))
# elif test == "TX-PROTOCOL Uplink Encrypted Payload":
#     print("todo")
elif test == "UL - Non Volatile Memory":
    send(bytes([8]))
elif test == "UL - Public Key":
    sigfox.public_key(True)
    send(bytes([1]))
    sigfox.public_key(False)
elif test == "UL - Frequency Distribution":
    sigfox.test_mode(SFX_TEST_MODE_TX_PROTOCOL, 14)
    # Loop 0 to (config & 0x7F)
    # bit 7 causes a delay between the frames
elif test == "UL - Frequency Synthesis":
    sigfox.test_mode(SFX_TEST_MODE_TX_SYNTH, 0)




################################################################################
elif test == "DL - Downlink":
    sigfox.test_mode(SFX_TEST_MODE_RX_PROTOCOL, 1)
elif test == "DL - Link Budget":
    sigfox.test_mode(SFX_TEST_MODE_RX_SENSI, 31) # 14:11
    # Loop 0 to (config x 10),
    # config should be 100 as per test protocol,
    # this takes very long
    # config = 1 takes about 127 seconds
    # config = 5 takes about 624 seconds
    # it seems after 30 frames (ie config = 3), RSA finished the test with INCONCLUSIVE
elif test == "DL - GFSK Receiver":
    print("Test Mode TX-BPSK has to be executed just before this test.")
    # print("Run test_mode(BPSK) before GFSK ... ")
    # sigfox.test_mode( SFX_TEST_MODE_TX_BPSK, 3)
    # print("... done. Click on \"Start send GFSK\" in RSA now")
    # sleep(2)
    # print("Run test_mode(GFSK) ...")
    sigfox.test_mode(SFX_TEST_MODE_RX_GFSK, 30) # 30 seconds timeout
    # print("... done.")
    print("rssi", sigfox.rssi())







################################################################################
elif test == "MyTest":
    for b in range(0, 10):
        x = utime.time()
        d = b % ( 0xff + 1 )
        retval = send(bytes([d]))
        print("sent after", utime.time() -x, "seconds")
        print("retval", retval)
        sleep(2)
elif test == "MyDownlink":
    x = utime.time()
    retval = send(bytes([0x0f]))
    print("sent after", utime.time() -x, "seconds")
    print("retval", retval)
    x = utime.time()
    input = s.recv(8)
    print("received after", utime.time() -x, "seconds")
    print("input", ubinascii.hexlify(input))
    print("rssi", sigfox.rssi())
elif test == "None":
    # do nothing
    None
else:
    print("ERROR: unknown test'", test, "''")

# pycom.heartbeat(True)
print("test completed after", utime.time() - start, "seconds")
