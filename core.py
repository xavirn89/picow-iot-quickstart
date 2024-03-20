import machine
import time
from lib.phew import get_ip_address

led = machine.Pin('LED', machine.Pin.OUT) #configure LED Pin as an output pin and create and led object for Pin class
ip = get_ip_address()

while True:
  led.value(True)  #turn on the LED
  print(f"LED is on, IP address: {ip}, waiting for 1 second...")
  time.sleep(1)   #wait for one second
  led.value(False)  #turn off the LED
  print(f"LED is off, IP address: {ip}, waiting for 1 second...")
  time.sleep(1)   #wait for one second
