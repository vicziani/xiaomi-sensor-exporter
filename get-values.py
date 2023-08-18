from bluepy import btle

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        databytes = bytearray(data)
        temperature = int.from_bytes(databytes[0:2],"little") / 100
        humidity = int.from_bytes(databytes[2:3],"little")
        battery = int.from_bytes(databytes[3:5],"little") / 1000
        print(f"Temperature: {temperature}, humidity: {humidity}, battery: {battery}")

mac = "24-48-8C-94-96-4C"
print(f"Connecting to {mac}")
connected = False
try:
    # Timeout not released: https://github.com/IanHarvey/bluepy/pull/374
    dev = btle.Peripheral(mac)
    connected = True
    print("Connection done...")
    delegate = MyDelegate()
    dev.setDelegate(delegate)
    print("Waiting for data...")
    dev.waitForNotifications(15.0)
except btle.BTLEDisconnectError as error:
    print(error)
finally:
    if connected:
        dev.disconnect()
