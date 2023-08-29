#!/usr/bin/python3

import argparse
import sys
import logging
import logging.config
import pprint
import yaml
from PIL import Image

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_sun
import sc6_general
import sc6_image
import sc6_config

class BlueCode:
    def __init__(self, fn, debug=False, config=None):

        if config == None:
            print("pulling config in BlueCode")
            mode = "prod"
            cfg = sc6_config.Config(mode = mode)
            config = cfg.get_config()

        self.fn = fn
        cdebug = config['Debug']
        self.debug = debug or cdebug
        self.config = config

        with open(config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)

        #  create logger
        self.logger = logging.getLogger('SC6BlueCode')
        self.logger.setLevel(logging.DEBUG)

        self.get_blue()

    def get_blue(self):

        start_row = self.config['BlueCode']['BlueTest']['StartRow']
        rows = self.config['BlueCode']['BlueTest']['Rows']
        sample = self.config['BlueCode']['Sampling']

        try:
            im = Image.open(self.fn)
        except FileNotFoundError:
            print("file {} missing, need an image ".format(self.fn))
            sys.exit()
        except:
            print("Can't process image file: {}".format(self.fn))
            sys.exit()

        width = im.width
        height = im.height

        cum_new_bc = 0
        cum_bc = 0
        cum_lum = 0
        cum_r = 0
        cum_g = 0
        cum_b = 0
        a_new_w = 0

        only_bc = False  # make False if playing with new maths for computing bluecode.

        for x in range(0, im.width, sample):
            for y in range(start_row, start_row + rows, sample):
                pixel_value = im.getpixel((x,y))
                # looking at the difference between blue and the average of red and green then
                # multiply by the luminosity to give weight to bright images
                # cum_bc += (b - ( (r + g) / 2)) * ( 2 * ((0.2126*r) + (0.7152*g) + (0.0722*b)))
                # don't use the green value for the difference 
                # because dusk and down can be very green
                r = pixel_value[0]
                g = pixel_value[1]
                b = pixel_value[2]
                cum_bc = cum_bc + (b - r ) * ( 2 * ((0.2126*r) + (0.7152*g) + (0.0722*b)))

                if not only_bc:
                   cum_lum = cum_lum + (0.2126*r) + (0.7152*g) + (0.0722*b)
                   cum_r = cum_r + r
                   cum_g = cum_g + g
                   cum_b = cum_b + b
                   # Base BlueCode: b - ( (r + g) / 2)
                   # Luminence: (0.2126*r) + (0.7152*g) + (0.0722*b)
                   # double the Luminence
                   if r >= 32 and g >= 32:
                       cum_new_bc = cum_new_bc + (b - g ) * ( 2 * ((0.2126*r) + (0.7152*g) + (0.0722*b)))

        scaling_factor = self.config['BlueCode']['CodeScaling']
        a_w = cum_bc / ( im.width * rows ) * scaling_factor
        if not only_bc:
            a_new_w = cum_new_bc / ( width * rows ) * scaling_factor
            cum_r = cum_r / ( width * rows )
            cum_g = cum_g / ( width * rows )
            cum_b = cum_b / ( width * rows )
            cum_lum = cum_lum / ( width * rows )

        if self.debug:
            self.logger.debug("Blue code: {}".format(a_w))
            self.logger.debug("New Blue code: {}".format(a_new_w))
            self.logger.debug("Luminence: {}".format(cum_lum))
            self.logger.debug("Cum R: {}".format(cum_r))
            self.logger.debug("Cum G: {}".format(cum_g))
            self.logger.debug("Cum B: {}".format(cum_b))

        self.bluecode = a_w
        self.x = a_new_w
        self.r = cum_r
        self.g = cum_g
        self.b = cum_b
        self.lum = cum_lum

if __name__ == '__main__':

    image_set = sc6_image.ImageSet()
    result = image_set.fetch()
    
    bluecode = BlueCode(image_set.output, "True")
    print("bluecode: ", bluecode.bluecode)
