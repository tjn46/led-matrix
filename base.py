import time
import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
import wifi
import socketpool
import adafruit_requests
import adafruit_ntp
from adafruit_display_text import label
from secrets import secrets

displayio.release_displays()

# MATRIX SETUP (32x32)
matrix = rgbmatrix.RGBMatrix(
    width=32,
    height=32,
    bit_depth=3,
    rgb_pins=[
        board.MTX_R1,
        board.MTX_G1,
        board.MTX_B1,
        board.MTX_R2,
        board.MTX_G2,
        board.MTX_B2,
    ],
    addr_pins=[
        board.MTX_ADDRA,
        board.MTX_ADDRB,
        board.MTX_ADDRC,
        board.MTX_ADDRD,
    ],
    clock_pin=board.MTX_CLK,
    latch_pin=board.MTX_LAT,
    output_enable_pin=board.MTX_OE,
)

display = framebufferio.FramebufferDisplay(matrix)
group = displayio.Group()
display.root_group = group

# WIFI
wifi.radio.connect(secrets["ssid"], secrets["password"])
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)

ntp = adafruit_ntp.NTP(pool, tz_offset=-5)  # EST

# PALETTE
palette = displayio.Palette(8)
palette[0] = 0x000000
palette[1] = 0xFFFFFF
palette[2] = 0xFF0000
palette[3] = 0x0000FF
palette[4] = 0x00FF00
palette[5] = 0xFFCC99
palette[6] = 0xFFA500
palette[7] = 0xAAAAAA

bmp = displayio.Bitmap(32, 32, 8)
tile = displayio.TileGrid(bmp, pixel_shader=palette)
group.append(tile)

# DRAW PIXEL ART
boy = [
"0011100",
"0122210",
"0155510",
"0044400",
"0044400",
"0020020",
"0200002",
]

girl = [
"0011100",
"0122210",
"0155510",
"0066600",
"0066600",
"0020020",
"0200002",
]

cat = [
"0030030",
"0030030",
"0011110",
"0111111",
"0110011",
"0001100",
]

def draw_sprite(sprite, x_offset, y_offset):
    for y, row in enumerate(sprite):
        for x, pixel in enumerate(row):
            if pixel != "0":
                bmp[x + x_offset, y + y_offset] = int(pixel)

# TEXT
time_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
time_label.x = 1
time_label.y = 6
group.append(time_label)

temp_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
temp_label.anchor_point = (1.0, 0)
temp_label.anchored_position = (31, 0)
group.append(temp_label)

def get_weather():
    url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}".format(
        secrets["openweather_location"],
        secrets["openweather_token"]
    )
    response = requests.get(url)
    data = response.json()
    response.close()
    return int(data["main"]["temp"])

# INITIAL DRAW
draw_sprite(boy, 2, 14)
draw_sprite(girl, 12, 14)
draw_sprite(cat, 22, 16)

temperature = get_weather()

while True:
    current_time = ntp.datetime
    hour = current_time.tm_hour
    minute = current_time.tm_min

    time_label.text = "{:02d}:{:02d}".format(hour, minute)
    temp_label.text = "{}F".format(temperature)

    time.sleep(30)
