import time

import board
import displayio
import framebufferio
import rgbmatrix
import terminalio
from adafruit_display_text import label


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
display = framebufferio.FramebufferDisplay(matrix, auto_refresh=True)

group = displayio.Group()
display.root_group = group

palette = displayio.Palette(4)
palette[0] = 0x000000
palette[1] = 0xFF3377
palette[2] = 0xFF77AA
palette[3] = 0xFFFFFF

bitmap = displayio.Bitmap(32, 32, 4)
group.append(displayio.TileGrid(bitmap, pixel_shader=palette))

heart = [
    "0011100011100",
    "0111110111110",
    "1111111111111",
    "1111111111111",
    "1111111111111",
    "0111111111110",
    "0011111111100",
    "0001111111000",
    "0000111110000",
    "0000011100000",
    "0000001000000",
]

heart_x = 9
heart_y = 2
for y, row in enumerate(heart):
    for x, pixel in enumerate(row):
        if pixel == "1":
            bitmap[heart_x + x, heart_y + y] = 1 + ((x + y) % 2)

message = label.Label(
    terminalio.FONT,
    text="Happy Birthday Mo!",
    color=0xFFFFFF,
)
message.y = 23
group.append(message)

while True:
    message_width = message.bounding_box[2]
    for x in range(32, -message_width - 1, -1):
        message.x = x
        time.sleep(0.06)
