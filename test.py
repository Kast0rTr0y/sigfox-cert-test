from network import Sigfox
import socket
import utime
import ubinascii
import pycom
import machine

##############################################################
## select the test you want to run by (un)commenting

## for use with Sigfox Radio Signal Analyzer
test = "TX-BPSK"
# test = "TX-PROTOCOL Protocol" # ca 123 seconds
# test = "TX-PROTOCOL Uplink Encrypted Payload"
# test = "TX-PROTOCOL NVM"
# test = "TX-PROTOCOL Public Key"
# test = "TX-PROTOCOL Frequency Distribution" # 4156 seconds (!) 1hour 9minutes
# test = "RX-PROTOCOL Downlink" # Use for both, "Start of Listening" and "End of Listening"
# test = "RX-GFSK"
# test = "RX-SENSI"
# test = "TX-SYNTH"  ## "UL - Frequency Synthesis"

## for use with Sigfox Network Emulator
test = "MyTest"
# test = "MyDownlink"


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

sigfox.public_key(True)
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
    if RCZ == Sigfox.RCZ2 or RCZ == Sigfox.RCZ4:
        delay = utime.time() - last
        if delay < wait:
            sleep(wait-delay)
    print("send", ubinascii.hexlify(msg))
    last = utime.time()
    r = s.send(msg)
    return r











############################################

# run test
start = utime.time()
# pycom.heartbeat(False)
# pycom.rgbled(0x000300)
if test == "TX-BPSK":
    e = sigfox.test_mode( SFX_TEST_MODE_TX_BPSK, 3)
    print("return value test_mode:", e)
elif test == "TX-PROTOCOL Protocol":
    send(bytes([0x1]))
    send(bytes([0x0]))
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

    # use the socket to send a Sigfox Out Of Band message
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, True)
    # send 1 bit
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, True)
    send('')
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, False)
    # disable Out-Of-Band to use the socket normally
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, False)
# elif test == "TX-PROTOCOL Uplink Encrypted Payload":
#     print("todo")
elif test == "TX-PROTOCOL NVM":
    send(bytes([7]))
elif test == "TX-PROTOCOL Public Key":
    sigfox.public_key(True)
    send(bytes([1]))
    sigfox.public_key(False)
elif test == "TX-PROTOCOL Frequency Distribution":
    e = sigfox.test_mode(SFX_TEST_MODE_TX_PROTOCOL, 34)
    # Loop 0 to (config & 0x7F)
    # bit 7 causes a delay between the frames
    print("return value test_mode:", e)
elif test == "RX-PROTOCOL Downlink":
    e = sigfox.test_mode(SFX_TEST_MODE_RX_PROTOCOL, 1)
    print("return value test_mode:", e)
elif test == "RX-GFSK":
    e = sigfox.test_mode(SFX_TEST_MODE_RX_GFSK, 30) # hex or dec 30?
    print("return value test_mode:", e)
    print("rssi", sigfox.rssi())
elif test == "RX-SENSI":
    e = sigfox.test_mode(SFX_TEST_MODE_RX_SENSI, 5)
    # Loop 0 to (config x 10),
    # config should be 100 as per test protocol,
    # this takes very long
    # config = 1 takes about 127 seconds
    # config = 5 takes about 624 seconds
    # it seems after 30 frames (ie config = 3), RSA finished the test with INCONCLUSIVE

    print("return value test_mode:", e)
elif test == "TX-SYNTH":
    e = sigfox.test_mode(SFX_TEST_MODE_TX_SYNTH, 0)
    print("return value test_mode:", e)



elif test == "MyTest":
    for b in range(0, 20):
        x = utime.time()
        d = b % ( 0xff + 1 )
        retval = send(bytes([d]))
        print("sent after", utime.time() -x, "seconds")
        print("retval", retval)
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
else:
    print("ERROR: unknown test'", test, "''")

# pycom.heartbeat(True)
print("test completed after", utime.time() - start, "seconds")
