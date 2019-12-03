from network import Sigfox
import socket
import utime
import ubinascii
import pycom

## select the test you want to run by (un)commenting
# test = "TX-BPSK"
test = "TX-PROTOCOL Protocol" # ca 123 seconds
# test = "TX-PROTOCOL Uplink Encrypted Payload"
# test = "TX-PROTOCOL NVM"
# test = "TX-PROTOCOL Frequency Distribution"
test = "Peter"
test = "Downlink"


# test mode constants for sigfox api
SFX_TEST_MODE_TX_BPSK     = 0
SFX_TEST_MODE_TX_PROTOCOL = 1
SFX_TEST_MODE_RX_PROTOCOL = 2
SFX_TEST_MODE_RX_GFSK     = 3
SFX_TEST_MODE_RX_SENSI    = 4
SFX_TEST_MODE_TX_SYNTH    = 5

# region
# Sigfox.RCZ1 # Europe, Oman & South Africa.
# Sigfox.RCZ2 # USA, Mexico & Brazil.
# Sigfox.RCZ3 # Japan.
# Sigfox.RCZ4 # Australia, New Zealand, Singapore, Taiwan, Hong Kong, Colombia & Argentina.
RCZ = Sigfox.RCZ1

sigfox = Sigfox(mode=Sigfox.SIGFOX, rcz=RCZ)
print("sigfox version:", sigfox.version())
print("sigfox ID:", ubinascii.hexlify(sigfox.id()))
print("sigfox PAC:", ubinascii.hexlify(sigfox.pac()))
print("sigfox region:", RCZ)

sigfox.public_key(True)
print("sigfox public key", sigfox.public_key())

s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
s.setblocking(True)
if ( test == "Downlink" ):
    # uplink + downlink
    print("sigfox link:", "up and down")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)
else:
    # configure it as uplink only
    print("sigfox link:", "uplink only")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

print("test:", test)​


# run test
start = utime.time()
# pycom.heartbeat(False)
# pycom.rgbled(0x000300)
if test == "TX-BPSK":
    sigfox.test_mode( SFX_TEST_MODE_TX_BPSK, 3)
elif test == "TX-PROTOCOL Protocol":
    s.send(bytes([0x1]))
    s.send(bytes([0x0]))
    s.send(bytes([0x40]))
    s.send(bytes([0x40, 0x41]))
    s.send(bytes([0x40, 0x41, 0x42]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A ]))
    s.send(bytes([0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46, 0x47, 0x48, 0x49, 0x4A, 0x4B ]))

    # use the socket to send a Sigfox Out Of Band message
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, True)
    # send 1 bit
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, True)
    s.send('')
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, False)
    # disable Out-Of-Band to use the socket normally
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, False)
elif test == "TX-PROTOCOL Uplink Encrypted Payload":
    print("todo")
elif test == "TX-PROTOCOL NVM":
    s.send(bytes([9]))
elif test == "TX-PROTOCOL Public Key":
    sigfox.public_key(True)
    s.send(bytes([1]))
    sigfox.public_key(False)
elif test == "TX-PROTOCOL Frequency Distribution":
    e = sigfox.test_mode(SFX_TEST_MODE_TX_PROTOCOL, 34) # stupid question? should it be 0x34 ? who knows
    print(e)

elif test == "Peter":
    for b in range(0,2):
        x = utime.time()
        #d = b % 0xff
        #print("send", ubinascii.hexlify(d))
        retval = s.send(bytes([b]))
        print("sent after", utime.time() -x, "seconds")
        print("retval", retval)
elif test == "Downlink":
    x = utime.time()
    retval = s.send(bytes([0x0f]))
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
