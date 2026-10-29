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

wifi.radio.connect(secrets["ssid"], secrets["password"])
pool = socketpool.SocketPool(wifi.radio)
requests = adafruit_requests.Session(pool)
ntp = adafruit_ntp.NTP(pool, tz_offset=0)

palette = displayio.Palette(8)
palette[0] = 0x000000
palette[1] = 0xFFFFFF
palette[2] = 0xFF8000
palette[3] = 0x8000FF
palette[4] = 0x00FF00
palette[5] = 0xFFFF00
palette[6] = 0xFF0000
palette[7] = 0xAAAAAA

bitmap = displayio.Bitmap(32, 32, 8)
group.append(displayio.TileGrid(bitmap, pixel_shader=palette))

ghost = [
    "00111100",
    "01111110",
    "11111111",
    "11311131",
    "11111111",
    "11111111",
    "11111111",
    "10111011",
]

pumpkin = [
    "000040000",
    "002222200",
    "022522520",
    "225222252",
    "225222252",
    "022522520",
    "002222200",
]

cat = [
    "3000003",
    "3300033",
    "3333333",
    "3633363",
    "3333333",
    "0300030",
    "3000003",
]

witch_hat = [
    "000030000",
    "000333000",
    "003333300",
    "033333330",
    "333333333",
    "000000000",
]


def draw_sprite(sprite, x_offset, y_offset):
    for y, row in enumerate(sprite):
        for x, pixel in enumerate(row):
            if pixel != "0":
                bitmap[x + x_offset, y + y_offset] = int(pixel)


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
    url = (
        "https://api.openweathermap.org/data/2.5/weather"
        "?q={}&units=imperial&appid={}".format(
            location,
            secrets["openweather_token"],
        )
    )
    response = requests.get(url)
    try:
        data = response.json()
    finally:
        response.close()
    return int(round(data["main"]["temp"]))


def is_new_york_dst(utc_time):
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


draw_sprite(ghost, 1, 17)
draw_sprite(pumpkin, 11, 20)
draw_sprite(witch_hat, 22, 14)
draw_sprite(cat, 23, 19)

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
