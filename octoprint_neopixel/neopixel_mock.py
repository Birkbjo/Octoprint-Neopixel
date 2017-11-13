# -*- coding: utf-8 -*-
import logging

class Adafruit_NeoPixel(object):
    def __init__(self,
                 logger,
                 num,
                 pin,
                 freq_hz=800000,
                 dma=5,
                 invert=False,
                 brightness=255,
                 channel=0,
                 strip_type='rgb'):
    
        self.count = num
        self._logger = logging.getLogger("octoprint.plugins.neopixel")
      #  self._logger.warn("Using mocked Neopixel-library!")
    def __del__(self):
        # Required because Python will complain about memory leaks
        # However there's no guarantee that "ws" will even be set
        # when the __del__ method for this class is reached.
        self._logger.debug("__DEL__")

    def _cleanup(self):
        # Clean up memory used by the library when not needed anymore.
        self._logger.debug("cleanup")

    def begin(self):
        """Initialize library, must be called once before other functions are
		called.
		"""
        self._logger.debug("Begin")

    def show(self):
        """Update the display with the data from the LED buffer."""
        self._logger.debug("show")

    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
		"""
        self._logger.debug("setPixelColor")

    def setPixelColorRGB(self, n, red, green, blue, white=0):
        """Set LED at position n to the provided red, green, and blue color.
		Each color component should be a value from 0 to 255 (where 0 is the
		lowest intensity and 255 is the highest intensity).
		"""
        self._logger.debug("setPixelColorRGB")

    def setBrightness(self, brightness):
        """Scale each LED in the buffer by the provided brightness.  A brightness
		of 0 is the darkest and 255 is the brightest.
		"""
        self._logger.debug("setBrightness")

    def getPixels(self):
        """Return an object which allows access to the LED display data as if 
		it were a sequence of 24-bit RGB values.
		"""
        self._logger.debug("getPixels")

    def numPixels(self):
        """Return the number of pixels in the display."""
        self._logger.debug("numPixels")
        return self.count

    def getPixelColor(self, n):
        """Get the 24-bit RGB color value for the LED at position n."""
        self._logger.debug("getPixelColor")

def Color(red, green, blue, white = 0):
	"""Convert the provided red, green, blue color to a 24-bit color value.
	Each color component should be a value 0-255 where 0 is the lowest intensity
	and 255 is the highest intensity.
	"""
	return (white << 24) | (red << 16)| (green << 8) | blue
