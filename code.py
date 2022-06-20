"""
Copyright MIT Licsense by Jonah Yolles-Murphy (@TG-Techie)
See licsense file for full text.

A bluetooth ID keyboard for clicking forwards and back while presenting.
- single click for next slide
- double click for previous slide
"""

import time

import board
import neopixel
import keypad



# === config ===
INPUT_PIN = board.SWITCH
# ==============

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


nx = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.25, auto_write=True)
nx[0] = CYAN


# used adafruit example as reference
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode


hid = HIDService()

device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="TG-Techie"
)
advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 0x03C1 # https://specificationrefs.bluetooth.com/assigned-values/Appearance%20Values.pdf
scan_response = Advertisement()
scan_response.complete_name = "Presenter Clicker"

ble = adafruit_ble.BLERadio()


keyboard = Keyboard(hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)

sw = keypad.Keys(
    pins=(INPUT_PIN,),
    value_when_pressed=False,
    pull=True,
)


def next_slide():
    keyboard.press(Keycode.RIGHT_ARROW)  # "Press"...
    keyboard.release_all()  # ..."Release"!
    print("next slide")


def previous_slide():
    keyboard.press(Keycode.LEFT_ARROW)  # "Press"...
    keyboard.release_all()  # ..."Release"!
    print("precious slide")


while True:
    if not ble.connected:
        print("Connecting...")
        nx[0] = RED
        ble.start_advertising(advertisement, scan_response)
        while not ble.connected:
            pass
        print("Connected!")
        # blink green twice
        nx[0] = GREEN
        time.sleep(1)
        nx[0] = BLACK

    # time.sleep(1)
    if (event := sw.events.get()) is not None and event.pressed:
        print("pressed")
        nx[0] = BLUE

        back_count = 0
        keep_going = True
        while keep_going:
            # print(last := time.monotonic())
            time.sleep(0.28)
            # get the next event until it is a pressed or a None
            while (
                next_event := sw.events.get()
            ) is not None and not next_event.pressed:
                pass

            if next_event is None:
                keep_going = False
                continue
            else:
                back_count += 1

        if back_count:
            for _ in range(back_count):
                previous_slide()
        else:
            next_slide()
        nx[0] = BLACK
