from network import Sigfox
from network import WLAN
from network import Server
import socket
import utime
import ubinascii
import pycom
import machine

utime.sleep(2)

##############################################################
## select the test you want to run by (un)commenting

## for use with Sigfox Radio Signal Analyzer
## Uplink
#test = "UL - RF" # ManualVerdict, same for Vnom/Vmin/Vmax
# test = "UL - Protocol" # [2 minutes]
# test = "UL - Non Volatile Memory" # ManualVerdict
# test = "UL - Public Key"
# test = "UL - Frequency Distribution" # [<= 15 minutes] (14:26)
# test = "UL - Frequency Synthesis"  ## [<= 2 minutes]
## Downlink:
# test = "DL - Downlink" # Use for any of "DL-Protocol", "DL-Start of Listening" and "DL-End of Listening"
# test = "DL - Link Budget" # DL-Link Budget [~ 5 minutes, then test is completed in RSA and you can reset the DUT]
#test = "DL - GFSK Receiver" # ManualVerdict [30 seconds], Test Mode TX-BPSK has to be executed just before this test.

## for use with Sigfox Network Emulator
test = "MyTest"
# test = "MyDownlink"
# test = "MyMockupDLProtocol"

# test = "None"



##############################################################
# ## select the region
RCZ = Sigfox.RCZ3


# RCZ1
#   Europe, Oman & South Africa.
#   UL= 868130000 Hz
#   DL= 869525000 Hz
#   DR= 100bps
#   Sigfox high limit recommendation: 16dBm
#   Low limit: 12dBm
# RCZ2
#   USA, Mexico & Brazil.
#   UL= 902200000 Hz
#   DL= 905200000 Hz
#   DR= 600bps
#   Sigfox high limit recommendation: 24dBm
#   Low limit: 20dBm
# RCZ3
#   Japan.
#   ARIB
#   UL= 923200000
#   DL= 922200000
#   DR= 100bps
#   Sigfox high limit recommendation: 16dBm
#   Low limit: 12dBm
# RCZ4
#   Australia, New Zealand, Singapore, Taiwan, Hong Kong, Colombia & Argentina.
#   UL= 920800000
#   DL= 922300000
#   DR= 600bps
#   Sigfox high limit recommendation: 24dBm
#   Low limit: 20dBm

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
print("sigfox rssi offset:", sigfox.rssi_offset())
print("sigfox info:")
sigfox.info() # normally prints nothing, but patched FW prints private key
#if RCZ == Sigfox.RCZ3:
#    sigfox.config((0x1, 0x2ee0, 0x100))
# sigfox.config((3,5000,0))
print("sigfox config:", sigfox.config()) # after reset RCZ3 defaults to (3, 5000, 0)

# by default put the device into private key mode
sigfox.public_key(False)
print("sigfox public key", sigfox.public_key())

s = socket.socket(socket.AF_SIGFOX, socket.SOCK_RAW)
s.setblocking(True)
# by default configure socket as uplink only
# print("socket:", "uplink only")
s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, False)

print("test:", test)
################################################################################






wait = 24 # how many seconds do we need to wait after every second frame (starting after the first) in RCZ2 and 4
last = -wait # when was the last sigfox message sent
rgb_send = 0x110000
rgb_idle = 0x000a00
rgb_test = 0x000011

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
        wait_so_far = utime.time() - last
        if wait_so_far < wait:
            sleep(wait - wait_so_far)
    else:
        pass
        sleep(1)
    print("send", ubinascii.hexlify(msg))
    pycom.rgbled(rgb_send)
    last = utime.time()
    r = s.send(msg)
    pycom.rgbled(rgb_idle)
    return r

def send_bit(b):
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_BIT, b)
    pycom.rgbled(rgb_send)
    s.send('')
    pycom.rgbled(rgb_idle)
    sleep(1)

def send_oob():
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, True)
    pycom.rgbled(rgb_send)
    s.send('')
    pycom.rgbled(rgb_idle)
    sleep(1)
    # disable Out-Of-Band to use the socket normally
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_OOB, False)


def test_mode(t,c):
    pycom.rgbled(rgb_test)
    sigfox.test_mode(t,c)
    pycom.rgbled(rgb_idle)










################################################################################
# run test
start = utime.time()
pycom.heartbeat(False)
if test == "UL - RF":
    test_mode( SFX_TEST_MODE_TX_BPSK, 1)
elif test == "UL - Protocol":
    # send a single bit: 0
    print("send False")
    send_bit(False)

    # send a single bit: 1
    print("send True")
    send_bit(True)

    # send an out of bound msg
    print("send OOB")
    # use the socket to send a Sigfox Out Of Band message
    send_oob()

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
    if RCZ == Sigfox.RCZ2 or RCZ == Sigfox.RCZ4:
        # send one bit
        send_bit(True)
    else:
        # if RCZ == Sigfox.RCZ3:
        #     sigfox.config((0x1, 0x2ee0, 0x100))
        # send one byte
        send(bytes([8]))
elif test == "UL - Public Key":
    sigfox.public_key(True)
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    send(bytes([1]))
    sigfox.public_key(False)
elif test == "UL - Frequency Distribution":
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    test_mode(SFX_TEST_MODE_TX_PROTOCOL, 14)
    # Loop 0 to (config & 0x7F)
    # bit 7 causes a delay between the frames
elif test == "UL - Frequency Synthesis":
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    test_mode(SFX_TEST_MODE_TX_SYNTH, 0)




################################################################################
elif test == "DL - Downlink":
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    test_mode(SFX_TEST_MODE_RX_PROTOCOL, 1)
elif test == "DL - Link Budget":
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    test_mode(SFX_TEST_MODE_RX_SENSI, 31) # 14:11
    # Loop 0 to (config x 10),
    # config should be 100 as per test protocol,
    # this takes very long
    # config = 1 takes about 127 seconds
    # config = 5 takes about 624 seconds
    # it seems after 30 frames (ie config = 3), RSA finished the test
elif test == "DL - GFSK Receiver":
    print("NB: Test Mode TX-BPSK has to be executed just before this test.")
    # print("Run test_mode(BPSK) before GFSK ... ")
    # sigfox.test_mode( SFX_TEST_MODE_TX_BPSK, 3)
    # print("... done. Click on \"Start send GFSK\" in RSA now")
    # sleep(2)
    # print("Run test_mode(GFSK) ...")
    test_mode(SFX_TEST_MODE_RX_GFSK, 30) # 30 seconds timeout
    # print("... done.")
    print("rssi", sigfox.rssi())







################################################################################
elif test == "MyTest":
    # print("a")
    # #send(bytes([1,2,3,4,5,6,7,8,9,0xa,0xb,0xc]))
    # send(bytes([7]))
    # print("b")
    # if RCZ == Sigfox.RCZ3:
    #     sigfox.config((0x1, 0x2ee0, 0x100))
    print(sigfox.config())
    r = machine.rng() & 0xff
    print("reconfiguring sigfox to use public key")
    sigfox.public_key(True)
    for b in range(0, 1):
        x = utime.time()
        d = b % ( 0xff + 1 )
        try:
            retval = send(bytes([0xac, r, d]))
            print("sent after", utime.time() -x, "seconds")
            print("retval", retval)
        except OSError as e:
            print("Exception caught:", e)

        rssi = sigfox.rssi()
        print("rssi", rssi)
        #sleep(2)
elif test == "MyDownlink":
    r = machine.rng() & 0xff
    rssis = {}
    # configure socket as uplink + downlink
    print("reconfiguring socket to RX mode (ie up AND down)")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)
    print("reconfiguring sigfox to use public key")
    sigfox.public_key(True)
    num_messages = 1
    for b in range(0, num_messages):
        x = utime.time()
        d = b % ( 0xff + 1 )
        print("sending message nr", b, "of", num_messages)
        try:
            retval = send(bytes([0xdd, r, d]))
            print("sent after", utime.time() -x, "seconds")
            print("retval", retval)
            x = utime.time()
            received = s.recv(8)
            print("received after", utime.time() -x, "seconds")
            print("received:", ubinascii.hexlify(received))
        except OSError as e:
            pycom.rgbled(0x550000)
            print("Exception caught:", e)

        rssi = sigfox.rssi()
        print("rssi", rssi)
        rssis[rssi] = rssis.get(rssi, 0) + 1
    median_number = num_messages / 2
    print("median_number=", median_number, "(", num_messages, ")")
    keys = sorted(list(rssis))
    ct = 0
    median_found = False
    median = 0
    print("rssi statistic:")
    for rssi in keys:
        ct += rssis[rssi]
        if not median_found and ct >= median_number:
            median_found = True
            median = rssi
        print("  ", rssi, ":", rssis[rssi])
    cumulated_delta = 0
    for rssi in keys:
        delta = abs(median - rssi)
        cumulated_delta += delta * rssis[rssi]

    print("median rssi=", median)
    print("cumulated delta=", cumulated_delta)
    print("delta=", cumulated_delta / num_messages)


elif test == "MyMockupDLProtocol":
    # an attempt to reimplement the DUT side of the "DL-Protocol" test of RSA
    # doesn't work completely, the frames come out with Hmac not ok and RSA doesn't send the downlink
    print("reconfiguring socket to RX mode (ie up AND down)")
    s.setsockopt(socket.SOL_SIGFOX, socket.SO_RX, True)

    print("reconfiguring sigfox to use public key")
    sigfox.public_key(True)

    retval = send(bytes([0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39, 0x3A, 0x3B]))
    print("sent after", utime.time() -x, "seconds")
    print("retval", retval)

    x = utime.time()
    received = s.recv(8)
    print("received after", utime.time() -x, "seconds")
    print("received:", ubinascii.hexlify(received))

    rssi = sigfox.rssi()
    print("rssi", rssi)

elif test == "None":
    # do nothing
    None
else:
    print("ERROR: unknown test'", test, "''")

# pycom.heartbeat(True)
print("test completed after", utime.time() - start, "seconds")
