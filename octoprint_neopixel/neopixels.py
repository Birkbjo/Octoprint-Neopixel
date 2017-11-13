# -*- coding: utf-8 -*-
import time
import readline
import sys
import argparse
import threading
from Queue import Queue, Empty
try:
    from neopixel import Adafruit_NeoPixel, Color
except ImportError as e:
    from .neopixel_mock import Adafruit_NeoPixel, Color
   
class Neopixels(object):
    def __init__(self,logger, num, pin = 18, freq_hz=800000, dma=5, brightness=255, invert=False, channel=0):
        """
        LED_COUNT      = 60      # Number of LED pixels.
        LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
        #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
        LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
        LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
        LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
        LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
        LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
        LED_STRIP      = "ws.WS2811_STRIP_GRB"   # Strip type and colour ordering"""
        
        self._logger = logger
        self.led_count = num
        self.strip = Adafruit_NeoPixel(num,pin,freq_hz, dma, invert, brightness, channel)
        
        self.colors = {
            "warm_white": Color(255, 172, 68)
        }
        self.animations = {
            "rainbow": self._rainbow, 
            "rainbowCycle": self._rainbowCycle, 
            "theaterChase": self._theaterChase,
            "theaterCaseRainbow": self._theaterChaseRainbow
        }
        
        self.queue = Queue()
        self.interrupt_event = threading.Event()
        self.stop_event = threading.Event()

        self.strip.begin()
        self._worker = Worker(logger, self.strip, self.queue, self.stop_event, self.interrupt_event)
        self._worker.start()

    def handle_async(self, lfunc, interrupt=True):
        ql = self.queue.qsize()
        if(interrupt == True and not self.queue.empty() and not self.interrupt_event.isSet()):
            self.interrupt_event.set()
        self.queue.put(lfunc)

    def run_animation(self, animation="rainbow", interrupt=False, kwargs=None):
        animation = str(animation)
        if not animation in self.animations:
            raise ValueError("Unknown animation " +animation)
        func = self.animations[animation]
        if kwargs is not None and "color" in kwargs:
            c = kwargs["color"]
            kwargs["color"] = Color(c[0], c[1], c[2])
        self._logger.info("Running " + func.__name__ + " with args " + str(kwargs))
        lfunc = (lambda: func()) if kwargs is None else (lambda: func(**kwargs))
        self.handle_async(lfunc, interrupt)

    # Define functions which animate LEDs in various ways.
    def colorWipe(strip, color, wait_ms=50):
        """Wipe color across display a pixel at a time."""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.trip.show()
            time.sleep(wait_ms/1000.0)

    def allWhite(self):
        for i in range(self._led_count):
            self.strip.setPixelColorRGB(i,255,255,255)
        self.strip.show()
    def off(self):
        for i in range(self.led_count):
            self.strip.setPixelColorRGB(i,0,0,0)
        self.strip.show()

    def allTo(self,r=255,g=255,b=255, color=None, wait = 0):
        for i in range(self.led_count):
            color = color or Color(r,g,b) 
            self.strip.setPixelColor(i, color)
            if wait > 0:
                time.sleep(wait)
                self.strip.show()
        self.strip.show()

    # ** ASYNC **
    def _theaterChase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation."""
        print "CHASE"
        for j in range(iterations):
            for q in range(3):
                for i in range(0,self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, color)
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

    def _wheel(self, pos):
        """Generate rainbow colors across 0-255 positions."""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)

    def _rainbow(self, wait_ms=20, iterations=1):
        """Draw rainbow that fades across all pixels at once."""
        print "RAINBOW"
        for j in range(256*iterations):
            if self.interrupt_event.isSet():
                print "INTERRUPTED"
                break
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self._wheel((i+j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def _rainbowCycle(self, wait_ms=20, iterations=5):
        """Draw rainbow that uniformly distributes itself across all pixels."""
        for j in range(256*iterations):
            for i in range(strip.numPixels()):
               self.strip.setPixelColor(i, self._wheel((int(i * 256 / self.strip.numPixels()) + j) & 255))
            self.strip.show()
            time.sleep(wait_ms/1000.0)

    def _theaterChaseRainbow(self, wait_ms=50):
        """Rainbow movie theater light style chaser animation."""
        for j in range(256):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                   self.strip.setPixelColor(i+q, self._wheel((i+j) % 255))
                self.strip.show()
                time.sleep(wait_ms/1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i+q, 0)

    def close(self):
        #interrupt running task
        self.interrupt_event.set()
        #stop loop and end-thread
        self.stop_event.set()
        self.strip.__del__()

    def clearQueue(self, interrupt=False):
        #consume items first
        while not self.queue.empty():
            self.queue.get()
        #then interrupt thead
        if(interrupt == True):
            self.interrupt_event.set()
        

class Worker(threading.Thread):
    """
    Simple Worker that can execute any lambda function via a Queue
    If the function has the same "interrupt-event" it can be interrupted by setting the flag
    """
    def __init__(self, logger, strip, queue, stop_event, interrupt_event):
        threading.Thread.__init__(self)
        self.daemon = True
        self.queue = queue
        self.stop_event = stop_event
        self.interrupt_event = interrupt_event
        self._logger = logger

    def run(self):
        self._logger.info("Running worker")
        while True and not self.stop_event.isSet():
            try:
                func = self.queue.get(block=True, timeout=2)
                self._logger.info("Worker got work!")
                func()
                self.queue.task_done()
                self.interrupt_event.clear()
            except Empty:
                pass
            except TypeError as e:
                self._logger.info(str(e))
        self._logger.info("Neopixel worker DONE")
