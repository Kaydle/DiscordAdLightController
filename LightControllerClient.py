import pystray

from PIL import Image, ImageDraw


# Create basic icon with pillow
def create_image(width, height, color1, color2):
    # Generate an image and draw a pattern
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2, 0, width, height // 2),
        fill=color2)
    dc.rectangle(
        (0, height // 2, width // 2, height),
        fill=color2)

    return image


""" Commands/Functions for tray options. """


def lights_off():
    event_list.append(0)


def lights_on():
    event_list.append(1)


def lights_function(func=None):
    # If light mode specified set to that otherwise will be random
    if func:
        event_list.append([3, func])
    else:
        event_list.append(2)


# close tray client from tray option
def close():
    x.stop()
    exit()


# set icon
x = pystray.Icon("Light Controller - py", title="Light Controller - py", icon=create_image(64, 64, 'black', 'white'))

# Tray Light options defined here

off = pystray.MenuItem("Turn Lights off", lights_off)
on = pystray.MenuItem("Turn Lights On", lights_on)
function = pystray.MenuItem("Change Light Function", lambda: lights_function(None))
bright_function = pystray.MenuItem("Set Lights to Bright", lambda: lights_function(7))
low_function = pystray.MenuItem("Set Lights to Low", lambda: lights_function(5))
close_program = pystray.MenuItem("Close", close)

# Set Name of tray client
title = pystray.MenuItem("Lights Controller - py", None)

Menu = pystray.Menu(off, on, function, bright_function, low_function, close_program)

x.menu = Menu

event_list = []

if __name__ == '__main__':
    x.run()
