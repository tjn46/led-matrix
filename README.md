# LED Matrix Displays

CircuitPython scripts for the Adafruit Matrix Portal and HUB75 RGB LED matrix panels. The intended display is a 32x32, 6 mm pitch panel.

## What the scripts do today

### `base.py` and `halloween.py`

Both scripts use the same 32x32 Matrix Portal setup, Wi-Fi, UTC NTP time converted to New York time, and OpenWeatherMap temperature lookup. They refresh the time and temperature together on a 30-second schedule.

- `base.py` draws the everyday boy, girl, and cat sprites.
- `halloween.py` draws a ghost, pumpkin, and witch-hat-wearing cat.

The 6 mm pitch does not change the software dimensions. The artwork and layout can be replaced or adjusted later without changing the basic matrix setup.

For development, `secrets.py` is provided in the project root with dummy placeholders. Replace them with your Wi-Fi name/password and OpenWeatherMap API key. When deploying, copy `secrets.py` to the root of the CIRCUITPY drive, next to the file you run as `code.py` (or `main.py`). The file defines a dictionary named `secrets`:

```python
secrets = {
    "ssid": "YOUR_WIFI_SSID",
    "password": "YOUR_WIFI_PASSWORD",
    "openweather_location": "New York,US",
    "openweather_token": "YOUR_OPENWEATHERMAP_API_KEY",
}
```

Replace the placeholders with your Wi-Fi name/password and OpenWeatherMap API key. The configured location `"New York,US"` asks OpenWeatherMap for New York, United States; the script requests `units=imperial`, so the displayed temperature is Fahrenheit. Create an OpenWeatherMap account and API key if you do not already have one.

Do not commit real credentials. This repository ignores `secrets.py`; keep your local copy out of public repositories and copy it to the CIRCUITPY drive when deploying. If the device is lost or shared, revoke/replace the API key and change the Wi-Fi password as appropriate.

The script requests UTC from NTP and converts it to New York time using current U.S. daylight-saving transition rules (second Sunday in March at 07:00 UTC through first Sunday in November at 06:00 UTC). This avoids a fixed UTC-5 offset and observes both EST and EDT. Network access, valid credentials, an active OpenWeatherMap API key, and the required CircuitPython libraries are needed. Network or API errors are not silently hidden and can stop the script.

### `birthday.py`

This is a separate, self-running birthday animation, not an add-on that `base.py` currently selects on a birthday. It:

- Creates a 32x32 matrix/bitmap using address pins A-D.
- Displays a pink heart and scrolls “Happy Birthday Mo!” across the bottom of the panel, repeating indefinitely.

It does not use Wi-Fi, check the date, or call `base.py`. Choosing which display to show for a holiday or special day will need a separate selection step. Each standalone display script initializes the matrix and enters a top-level infinite loop, so they are not reusable display functions; a clean date-based selector will require moving each display into a callable function or otherwise arranging for the entry point to choose one before its display loop starts.

`halloween.py` and `birthday.py` are also standalone displays. They do not automatically replace `base.py` on a holiday; choose which script to copy to `code.py`, or add a selector as the device entry point.

## Offline 32x32 simulator

Open [matrix_preview.ipynb](./matrix_preview.ipynb) in VS Code or Jupyter and run its cells from top to bottom using a Jupyter kernel with IPython available. Select `base`, `halloween`, `birthday`, or `custom`; the notebook renders an enlarged 32x32 grid with playback, stepping, seeking, and speed controls. For base and Halloween, it simulates clock/weather display updates using the configured start time and sample temperatures. Birthday preview advances through its scrolling message.

The notebook uses [matrix_simulator.py](./matrix_simulator.py) and does not import or execute the hardware scripts, connect to Wi-Fi, or contact NTP/weather services. Its compact text font and rendered colors are visual approximations, not a CircuitPython emulator. To preview another design, choose `custom` and edit `draw_custom(display, frame_index)` in the notebook: use `display.pixel(x, y, color_index)`, `display.sprite(rows, x, y)`, `display.text(text, x, y, color=1)`, and `display.clear()`. Custom scripts need to use this preview API; arbitrary CircuitPython scripts cannot be run unchanged.

## Hardware notes

The scripts use the 32x32 matrix dimensions and address-pin count for the stated hardware. Verify the panel orientation and colors on the physical display, then adjust the sprites, text, and layout to suit your design.

The panel's 6 mm pitch affects its physical size, not the pixel coordinate system: a 32x32 panel still has x and y coordinates from 0 through 31.

## CircuitPython setup

Install CircuitPython for the Matrix Portal M4 and copy the required Adafruit libraries and dependencies into the device's `lib` folder. The scripts use `adafruit_requests`, `adafruit_ntp`, and `adafruit_display_text` in addition to CircuitPython's board, display, RGB-matrix, and Wi-Fi modules. Both `base.py` and `halloween.py` need `secrets.py`; keep real credentials off public version control.

CircuitPython automatically starts `code.py` (or `main.py`) on the device. To run one of these scripts directly, copy it as the entry-point filename. A future date-based selector should be the entry point and choose a display before starting its loop.

Use an appropriate regulated 5V supply for the matrix. RGB panels can draw substantial current; follow the panel and Matrix Portal wiring/power instructions, and do not assume a computer's USB port can safely supply the panel's full load.

## Hardware references

- [Adafruit Matrix Portal M4 guide](https://learn.adafruit.com/adafruit-matrixportal-m4/overview)
- [Adafruit RGB LED matrices with CircuitPython guide](https://learn.adafruit.com/rgb-led-matrices-matrix-panels-with-circuitpython)
