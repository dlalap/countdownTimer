import RPi.GPIO as GPIO
import time
import datetime as dt
import requests

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.virtual import viewport, sevensegment
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT, LCD_FONT

class CountdownTimer():
    def __init__(self):
        self.serial = None
        self.initializeSerial()
        self.initializeGPIO()
        self.countdownActive = False
        self.buttonPressed = False
        self.diff = dt.timedelta()
        self.future = dt.datetime.now()
        self.currentColor = "white"
        self.main()

    def initializeSerial(self):
        if self.serial is not None:
            return

        self.serial = spi(
            port=0,
            device=0,
            gpio=noop()
        )
        self.device = max7219(
                self.serial,
                width=48,
                height=8
            )
        # self.seg = sevensegment(self.device)

    def initializeGPIO(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(10, GPIO.RISING, callback=self.buttonCallback)
        
    
    def buttonCallback(self, channel):
        self.buttonPressed = True
        print(f'Button has been pressed! channel = {channel}')
        self.countdownActive = False
        self.displayText("")
        self.buttonPressed = False
        self.startCountdown(5)

    def getMilliseconds(self, tDelta):

        totalMs = tDelta.days * 1e3 * 3600 * 24
        totalMs += tDelta.seconds * 1e3
        totalMs += tDelta.microseconds / 1e3 

        return totalMs

    def startCountdown(self, sec=30):
        now = dt.datetime.now()
        self.futureDate = now + dt.timedelta(seconds=sec)
        self.diff = self.futureDate - now
        self.countdownActive = True

    def main(self):
        while True: 
            time.sleep(0.001)
            if self.countdownActive and self.getMilliseconds(self.diff) > 0:
                self.setLight('white')
                if self.buttonPressed:
                    continue 
                minutes = self.diff.seconds // 60
                seconds = self.diff.seconds + self.diff.microseconds/1e6
                parsedText = f'{minutes:02}.{seconds:06.3F}'
                # print(parsedText)
                self.displayText(parsedText)
                self.diff = self.futureDate - dt.datetime.now()
            elif self.getMilliseconds(self.diff) <= 0: 
                self.countdownActive = False
                self.displayOutOfTimeMessage()
            else:
                self.displayText("RESETING")

    def displayOutOfTimeMessage(self):
        self.setLight('red')
        self.displayText('DRINK!')

    def displayText(self, message):
         # self.seg.text = text 
        with canvas(self.device) as draw:
            text(draw, (0, 0), message, fill="white", font=proportional(LCD_FONT))

    def setLight(self, color):
        if color == self.currentColor:
            return
        
        if color == 'red':
            # get red     
            res = requests.get('http://localhost:5000/on/saturation/100')

        if color == 'white':
            # get white
            res = requests.get('http://localhost:5000/on/saturation/0')

        self.currentColor = color
        print(f'Response: {res.text}')
         
if __name__ == '__main__':
    try:
        while True:
            timer = CountdownTimer()
    except KeyboardInterrupt:
        GPIO.cleanup()
    finally:
        requests.get('http://localhost:5000/on/saturation/0')
