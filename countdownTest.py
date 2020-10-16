import time
import datetime as dt

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT


def main():
    serial = spi(port=0, device=0, gpio=noop())
    # device = max7219(
    #        serial,
    #        cascaded=4,
    #        block_orientation=0,
    #        rotate=0,
    #        blocks_arranged_in_reverse_order=False
    #    ) 
    device = max7219(
            serial,
            width=48,
            height=8
        )
    #show_message(device, "HEY THERE", fill="white", font=proportional(CP437_FONT))
    with canvas(device) as draw:
        text(draw, (0, 0), "00:00.000", fill="white", font=proportional(TINY_FONT) )
    #seg.text = "HEYTHERE"
    
    time.sleep(5)
    device.cleanup()

def countdown(seconds):
    serial = spi(port=0, device=0, gpio=noop())
    # device = max7219(serial, cascaded=1)
    # seg = sevensegment(device)

    device = max7219(serial, width=48, height=8)

    now = dt.datetime.now()
    futureDate = now + dt.timedelta(seconds = seconds)
    diff = futureDate - now
    
    # while diff.seconds > 0 or diff.microseconds > 100:
    while getMilliseconds(diff) > 0:
        # print(getMilliseconds(diff))

        parsedText = f'{diff.seconds // 60:02}.' \
                f'{diff.seconds + diff.microseconds / 1e6:06.3F}' 

        # seg.text = parsedText
        # text(draw, (0, 0), parsedText, fill="white", font=proportional(TINY_FONT) )
        writeMessage(device, parsedText)
        diff = futureDate - dt.datetime.now()

    for i in range(5):
        # seg.text = "SHOTS"
        writeMessage(device, "SHOTS")
        time.sleep(1)
        # seg.text = ""
        writeMessage(device, "")
        time.sleep(1)
    device.cleanup()

def writeMessage(deviceObject, message):
    with canvas(deviceObject) as draw:
        text(draw, (0, 0), message, fill="white", font=proportional(LCD_FONT))
        

def getMilliseconds(tDelta):
    daysInMs = tDelta.days * 1e3 * 3600 * 24
    secondsInMs = tDelta.seconds * 1e3
    uSecondsInMs = tDelta.microseconds / 1e3

    totalMs = daysInMs + secondsInMs + uSecondsInMs
    return totalMs

if __name__ == '__main__':
    countdown(5)
    # main()
