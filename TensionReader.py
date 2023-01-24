"""
Log and Display Tension
"""
import board
import displayio
from adafruit_display_text import label
import adafruit_displayio_sh1107
import time
import adafruit_sdcard
import busio
import digitalio
import storage
import terminalio

# from adafruit_display_shapes.circle import Circle   NEED THIS I THINK

# Import packages for tension see https://github.com/endail/hx711-rpi-py
# from HX711 import *

""" Set up the time on the system, will this need to be tuned every day? """
# days = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
# while False:   # change to True if you want to write the time!
# year, mon, date, hour, min, sec, wday, yday, isdst
# t = time.struct_time((2022,  06,   20,   10,  25,  0,    1,   -1,    -1))
# you must set year, mon, date, hour, min, sec and weekday
# yearday is not supported, isdst can be set
# but we don't do anything with it at this time
#  print("Setting time to:", t)     # uncomment for debugging
# rtc.datetime = t
# print()

""" Set up display """
displayio.release_displays()
i2c = board.I2C()
display_bus = displayio.I2CDisplay(i2c, device_address=0x3C)
w = 128
h = 64
b = 2
display = adafruit_displayio_sh1107.SH1107(display_bus, width=w, height=h, rotation=0)
splash = displayio.Group()
display.show(splash)
color_bitmap = displayio.Bitmap(w, h, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White
bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
splash.append(bg_sprite)
inner_bitmap = displayio.Bitmap(w - b * 2, h - b * 2, 1)
inner_palette = displayio.Palette(1)
inner_palette[0] = 0x000000  # Black
inner_sprite = displayio.TileGrid(
    inner_bitmap, pixel_shader=inner_palette, x=b, y=b)
splash.append(inner_sprite)

""" Set up buttons and filesystem """
# Use any pin that is not taken by SPI
SD_CS = board.D10
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT

# Connect to the card and mount the filesystem.
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
cs = digitalio.DigitalInOut(SD_CS)
sdcard = adafruit_sdcard.SDCard(spi, cs)
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

# Set up button pins
pin_a = digitalio.DigitalInOut(board.D9)
pin_a.direction = digitalio.Direction.INPUT
pin_a.pull = digitalio.Pull.UP

pin_b = digitalio.DigitalInOut(board.D6)
pin_b.direction = digitalio.Direction.INPUT
pin_b.pull = digitalio.Pull.UP

while True:
    pass 
"""Set up tension reader """
# hx = SimpleHX711(2, 3, -370, -367471)
# hx.setUnit(Mass.Unit.OZ)
# hx.zero()

""" Create Animal class """
class Animal():
    def __init__(self, directory, aquisition):
        """Initialize animal class variables"""
        self.string_save = directory + str(time.time()) + ".txt"
        self.aquisition = aquisition
        self.spt = time.time() + 2*60*60  # 2 hours converted to seconds
        self.stop = False
    def record(self):
        # Get the tension and time, save to file, update screen
        self.tension = 0
        # self.tension = float(hx.weight(35)) #get median weight from 35 samples
        self.ct = time.time()  # Time is being recorded as a floating point number
        current_input = str(self.ct) + ',' + str(self.tension)
        self.file = open(self.string_save, "w")
        self.file.write(current_input)
        self.file.close()
        time.sleep(self.aquisition)
        self.set_screen()
    def stop_recording(self):
        self.stop = True
        return

    def set_screen(self):
        # updates screen every X seconds based on aquisition
        if self.stop:
            # Update screen with time, tension, battery life
            ts = "Time: "
            Time_text = label.Label(terminalio.FONT, text=ts, color=0xFFFFFF, x=5, y=21)
            splash.append(Time_text)
            
            tns = "Tension: "
            tnst = label.Label(terminalio.FONT, text=tns, color=0xFFFFFF, x=5, y=42)
            splash.append(tnst)

            bs = "Battery: " + str(100) + "%"
            bt = label.Label(terminalio.FONT, text=bs, color=0xFFFFFF, x=70, y=42)
            splash.append(bt)

            rs = "Rec"
            rt = label.Label(terminalio.FONT, text=rs, color=0xFFFFFF, x=70, y=21)
            splash.append(rt)

            # circle = Circle(90, 21, 10, fill=0x00FF00, outline=0xFF00FF)
            # splash.append(circle)
        else:
            # Update screen with time, tension, battery life
            ts = "Time: " + str(self.ct - time.time())
            Time_text = label.Label(terminalio.FONT, text=ts, color=0xFFFFFF, x=5, y=21)
            splash.append(Time_text)

            tns = "Tension: " + str(self.tensio
            tnst = label.Label(terminalio.FONT, text=tns, color=0xFFFFFF, x=5, y=42)
            splash.append(tnst)

            bs = "Battery: " + str(100) + "%"
            bt = label.Label(terminalio.FONT, text=bs, color=0xFFFFFF, x=70, y=42)
            splash.append(bt)

            rs = "Rec"
            rt = label.Label(terminalio.FONT, text=rs, color=0xFFFFFF, x=70, y=21)
            splash.append(rt)

            # circle = Circle(90, 21, 2, fill=0x00FF00, outline=0xFF00FF)
            # splash.append(circle)
        return

flag = False
while True:  # Keeps code running 24/7 waiting for button inputs
    if pin_a.value is False:
        flag = True
        directory = "/sd/"
        aquisition = 0.03
        ca = Animal(directory, aquisition)

    while flag:  # Determins when current animal is finishid
        ca.record()
        if (pin_b.value is False) or (ca.ct > ca.spt):
            ca.stop_recording()
            flag = False
            del ca
