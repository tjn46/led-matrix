"""Offline 32x32 frame renderer for the LED matrix preview notebook."""

BASE_PALETTE = [
    "#000000",
    "#ffffff",
    "#ff0000",
    "#0000ff",
    "#00ff00",
    "#ffcc99",
    "#ffa500",
    "#aaaaaa",
]

HALLOWEEN_PALETTE = [
    "#000000",
    "#ffffff",
    "#ff8000",
    "#8000ff",
    "#00ff00",
    "#ffff00",
    "#ff0000",
    "#aaaaaa",
]

BIRTHDAY_PALETTE = [
    "#000000",
    "#ff3377",
    "#ff77aa",
    "#ffffff",
]

CUSTOM_PALETTE = [
    "#000000",
    "#ffffff",
    "#ff8000",
    "#8000ff",
    "#00ff00",
    "#ffff00",
    "#ff0000",
    "#aaaaaa",
]

FONT_3X5 = {
    " ": ("000", "000", "000", "000", "000"),
    "!": ("010", "010", "010", "000", "010"),
    "-": ("000", "000", "111", "000", "000"),
    ":": ("000", "010", "000", "010", "000"),
    "?": ("110", "001", "010", "000", "010"),
    "0": ("111", "101", "101", "101", "111"),
    "1": ("010", "110", "010", "010", "111"),
    "2": ("110", "001", "111", "100", "111"),
    "3": ("110", "001", "011", "001", "110"),
    "4": ("101", "101", "111", "001", "001"),
    "5": ("111", "100", "110", "001", "110"),
    "6": ("011", "100", "110", "101", "010"),
    "7": ("111", "001", "010", "010", "010"),
    "8": ("010", "101", "010", "101", "010"),
    "9": ("010", "101", "011", "001", "110"),
    "A": ("010", "101", "111", "101", "101"),
    "B": ("110", "101", "110", "101", "110"),
    "D": ("110", "101", "101", "101", "110"),
    "F": ("111", "100", "110", "100", "100"),
    "H": ("101", "101", "111", "101", "101"),
    "I": ("111", "010", "010", "010", "111"),
    "M": ("101", "111", "111", "101", "101"),
    "O": ("010", "101", "101", "101", "010"),
    "P": ("110", "101", "110", "100", "100"),
    "R": ("110", "101", "110", "101", "101"),
    "T": ("111", "010", "010", "010", "010"),
    "Y": ("101", "101", "010", "010", "010"),
}

BASE_SPRITES = (
    (2, 14, (
        "0011100",
        "0122210",
        "0155510",
        "0044400",
        "0044400",
        "0020020",
        "0200002",
    )),
    (12, 14, (
        "0011100",
        "0122210",
        "0155510",
        "0066600",
        "0066600",
        "0020020",
        "0200002",
    )),
    (22, 16, (
        "0030030",
        "0030030",
        "0011110",
        "0111111",
        "0110011",
        "0001100",
    )),
)

HALLOWEEN_SPRITES = (
    (1, 17, (
        "00111100",
        "01111110",
        "11111111",
        "11311131",
        "11111111",
        "11111111",
        "11111111",
        "10111011",
    )),
    (11, 20, (
        "000040000",
        "002222200",
        "022522520",
        "225222252",
        "225222252",
        "022522520",
        "002222200",
    )),
    (22, 14, (
        "000030000",
        "000333000",
        "003333300",
        "033333330",
        "333333333",
        "000000000",
    )),
    (23, 19, (
        "3000003",
        "3300033",
        "3333333",
        "3633363",
        "3333333",
        "0300030",
        "3000003",
    )),
)

HEART = (
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
)


class PreviewDisplay:
    """Simple drawing surface shared by built-in and custom preview scenes."""

    width = 32
    height = 32

    def __init__(self, palette):
        if not palette or palette[0].lower() != "#000000":
            raise ValueError("Palette index 0 must be black.")
        self.palette = tuple(palette)
        self.clear()

    def clear(self):
        self.pixels = [[0 for _ in range(self.width)] for _ in range(self.height)]

    def pixel(self, x, y, color):
        """Set a palette-indexed pixel; out-of-panel coordinates are clipped."""
        if 0 <= x < self.width and 0 <= y < self.height:
            if not 0 <= color < len(self.palette):
                raise ValueError("Pixel color index is not in this palette.")
            self.pixels[y][x] = color

    def sprite(self, rows, x, y):
        """Draw digit-string or integer-row sprite art; zero is transparent."""
        for row_offset, row in enumerate(rows):
            for col_offset, value in enumerate(row):
                color = int(value)
                if color:
                    self.pixel(x + col_offset, y + row_offset, color)

    def text(self, value, x, y, color=1, align="left"):
        """Draw compact 3x5 text (uppercase display font) at the given origin."""
        text = str(value).upper()
        text_width = max(0, len(text) * 4 - 1)
        if align == "right":
            x -= text_width
        elif align == "center":
            x -= text_width // 2
        elif align != "left":
            raise ValueError("align must be 'left', 'center', or 'right'.")

        for char_index, char in enumerate(text):
            glyph = FONT_3X5.get(char, FONT_3X5["?"])
            for row_offset, row in enumerate(glyph):
                for col_offset, value in enumerate(row):
                    if value == "1":
                        self.pixel(
                            x + char_index * 4 + col_offset,
                            y + row_offset,
                            color,
                        )

    def frame(self):
        """Return a detached row-major pixel frame as palette indices."""
        return [pixel for row in self.pixels for pixel in row]


def _draw_sprites(display, sprites):
    for x, y, sprite in sprites:
        display.sprite(sprite, x, y)


def _clock_and_weather(display, clock_minutes, temperature):
    hour = (clock_minutes // 60) % 24
    minute = clock_minutes % 60
    display.text("{:02d}:{:02d}".format(hour, minute), 1, 1)
    display.text("{}F".format(temperature), 31, 1, align="right")


def render_frames(
    scene,
    frame_count,
    start_time="17:25",
    temperatures=(56, 57, 58, 57),
    custom_draw=None,
):
    """Render a sequence of 32x32 frames without importing hardware scripts."""
    if frame_count < 1:
        raise ValueError("frame_count must be at least 1.")
    if not temperatures:
        raise ValueError("Provide at least one sample temperature.")

    display_name = scene.lower()
    if display_name == "base":
        palette = BASE_PALETTE
    elif display_name == "halloween":
        palette = HALLOWEEN_PALETTE
    elif display_name == "birthday":
        palette = BIRTHDAY_PALETTE
    elif display_name == "custom":
        if custom_draw is None:
            raise ValueError("Define custom_draw(display, frame_index) first.")
        palette = CUSTOM_PALETTE
    else:
        raise ValueError("scene must be base, halloween, birthday, or custom.")

    display = PreviewDisplay(palette)
    frames = []
    notes = []

    if display_name in ("base", "halloween"):
        try:
            start_hour, start_minute = (
                int(part) for part in start_time.split(":")
            )
        except (AttributeError, ValueError):
            raise ValueError("start_time must use 24-hour HH:MM format.")
        if not 0 <= start_hour < 24 or not 0 <= start_minute < 60:
            raise ValueError("start_time must use 24-hour HH:MM format.")
        start_minutes = start_hour * 60 + start_minute

    for frame_index in range(frame_count):
        display.clear()

        if display_name == "base":
            _draw_sprites(display, BASE_SPRITES)
            temperature = temperatures[frame_index % len(temperatures)]
            clock_minutes = start_minutes + frame_index // 2
            _clock_and_weather(
                display,
                clock_minutes,
                temperature,
            )
            notes.append(
                "Simulated update {:02d}: {:02d}:{:02d}, sample temperature {} F".format(
                    frame_index,
                    (clock_minutes // 60) % 24,
                    clock_minutes % 60,
                    temperature,
                )
            )
        elif display_name == "halloween":
            _draw_sprites(display, HALLOWEEN_SPRITES)
            temperature = temperatures[frame_index % len(temperatures)]
            clock_minutes = start_minutes + frame_index // 2
            _clock_and_weather(
                display,
                clock_minutes,
                temperature,
            )
            notes.append(
                "Simulated update {:02d}: {:02d}:{:02d}, sample temperature {} F".format(
                    frame_index,
                    (clock_minutes // 60) % 24,
                    clock_minutes % 60,
                    temperature,
                )
            )
        elif display_name == "birthday":
            for y, row in enumerate(HEART):
                for x, value in enumerate(row):
                    if value == "1":
                        display.pixel(9 + x, 2 + y, 1 + ((x + y) % 2))
            message = "Happy Birthday Mo!"
            text_width = len(message) * 4 - 1
            start_x = display.width
            stop_x = -text_width
            scroll_x = start_x - (
                frame_index % (start_x - stop_x + 1)
            )
            display.text(message, scroll_x, 23)
            notes.append(
                "Scroll frame {:02d}: message x={}".format(frame_index, scroll_x)
            )
        else:
            custom_draw(display, frame_index)
            notes.append("Custom frame {:02d}".format(frame_index))

        frames.append(display.frame())

    return {
        "scene": display_name,
        "palette": palette,
        "frames": frames,
        "notes": notes,
    }
