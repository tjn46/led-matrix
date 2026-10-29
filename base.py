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

ntp = adafruit_ntp.NTP(pool, tz_offset=0)

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
    location = secrets["openweather_location"].replace(" ", "%20")
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}".format(
        location,
        secrets["openweather_token"]
    )
    response = requests.get(url)
    try:
        data = response.json()
    finally:
        response.close()
    return int(round(data["main"]["temp"]))

def is_new_york_dst(utc_time):
    # CircuitPython uses Monday=0; U.S. DST changes at 07:00 UTC in March and 06:00 UTC in November.
    month = utc_time.tm_mon
    if 3 < month < 11:
        return True
    if month < 3 or month > 11:
        return False

    first_day_weekday = (
        utc_time.tm_wday - ((utc_time.tm_mday - 1) % 7)
    ) % 7
    first_sunday = 1 + ((6 - first_day_weekday) % 7)

    if month == 3:
        second_sunday = first_sunday + 7
        return utc_time.tm_mday > second_sunday or (
            utc_time.tm_mday == second_sunday and utc_time.tm_hour >= 7
        )

    return utc_time.tm_mday < first_sunday or (
        utc_time.tm_mday == first_sunday and utc_time.tm_hour < 6
    )

def format_new_york_time(utc_time):
    offset = -4 if is_new_york_dst(utc_time) else -5
    hour = (utc_time.tm_hour + offset) % 24
    return "{:02d}:{:02d}".format(hour, utc_time.tm_min)

# INITIAL DRAW
draw_sprite(boy, 2, 14)
draw_sprite(girl, 12, 14)
draw_sprite(cat, 22, 16)

next_update = time.monotonic()
while True:
    current_time = ntp.datetime
    time_label.text = format_new_york_time(current_time)
    temperature = get_weather()
    temp_label.text = "{}F".format(temperature)

    next_update += 30
    delay = next_update - time.monotonic()
    if delay > 0:
        time.sleep(delay)
    else:
        next_update = time.monotonic()
