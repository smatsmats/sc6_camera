#!/usr/bin/python3

# from datetime import datetime
# from datetime import timedelta
# import pytz
# import astral
# from astral import LocationInfo
# from astral.sun import sun

import argparse
import os
import sys
import logging
import logging.config
# import pprint
import yaml
from PIL import Image
from stat import *

# use SC6::Cam::General
# use SC6::Cam::BlueCode
# use SC6::Cam::Overlay
# use SC6::Cam::GStore
#

sys.path.append('/usr/local/cam/lib/pythonlib')
# import bucket_shiz
import sc6_sun
import sc6_general

with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

#  create logger
logger = logging.getLogger('SC6Image')


class ImageSet:
    def __init__(self):

        # obs, fix this
        self.debug = True

        mysun = sc6_sun.SC6Sun()
        self.dt = mysun.get_dt()
        self.dt_epoch = mysun.dt_epoch

        # size isn't really used yet, so we just set it staticallyk
        self.size = "orig"
        # set this somewhere else
        self.mode = "prod"

        # these are the files that are saved
        image_dir = sc6_general.get_image_dir(self.dt, "orig", self.mode)
        self.output = "{}image{}_orig.jpg".format(image_dir, self.dt_epoch)
        image_dir = sc6_general.get_image_dir(self.dt, "50pct", self.mode)
        self.output_50pct = "{}image{}_50pct.jpg".format(image_dir, self.dt_epoch)

        # public version of image (with mask) saved for one day so we can make video
        public_image_dir = sc6_general.get_image_dir(self.dt, "public", self.mode)
        self.public_output = "{}image{}_orig.jpg".format(public_image_dir, self.dt_epoch)
        public_image_dir = sc6_general.get_image_dir(self.dt, "public_50pct", self.mode)
        self.public_output_50pct = "{}image{}_50pct.jpg".format(public_image_dir, self.dt_epoch)

        # these are the files / links used on the web page
        www_dir = sc6_general.get_www_dir(self.size, self.mode)
        www_public_dir = sc6_general.get_www_public_dir(self.size, self.mode)
        self.www_image_orig = os.path.join(www_dir, config['Image']['File']['orig'])
        self.www_image_50pct = os.path.join(www_dir, config['Image']['File']['50pct'])
        self.www_public_image_orig = os.path.join(www_public_dir, config['Image']['File']['orig'])
        self.www_public_image_50pct = os.path.join(www_public_dir, config['Image']['File']['50pct'])

        self.public_mask = self.load_privacy_mask()

    def load_privacy_mask(self):
        if not config['Public']['Enable']:
            return None

        mask_file = config['Public']['MaskFile']
        try:
            mask_image = Image.open(mask_file)
        except FileNotFoundError:
            print("file {} missing, need a ['Public']['MaskFile']".format(mask_file))
            os.exit()
        except:
            print("Can't process mask file: {}".format(mask_file))
            os.exit()
        return mask_image

    def fetch(self):

        command = config['Image']['Fetch']['Command']
        args = config['Image']['Fetch']['ArgsList']

        cmd = [command]
        cmd = cmd + args
        cmd.append(self.output)

        ret = sc6_general.run_cmd(cmd, self.debug)

        if ret == 0 and os.path.exists(self.output):
            size = os.path.getsize(self.output)
            if size >= config['Image']['MinSize']:
                self.success = 1
            else:
                self.success = 0
                try:
                    os.unlink(self.output)
                except OSError:
                    print("return code is not 0 ret or file is too small")
                    pass

        return self.success



# sub resizes_and_links
#     my (self) = @_
#
#     output_orig = self.output
#     output_50pct = self.output_50pct
#     www_image_orig = self.www_image_orig
#     www_image_50pct = self.www_image_50pct
#     public_output_orig = self.public_output
#     public_output_50pct = self.public_output_50pct
#     www_public_image_orig = self.www_public_image_orig
#     www_public_image_50pct = self.www_public_image_50pct
#
#     scale_cmd = "convert -scale 50% output_orig output_50pct"
#     i_do_cmd(self, scale_cmd)
#     scale_cmd = "convert -scale 50% public_output_orig public_output_50pct"
#     i_do_cmd(self, scale_cmd)
#
#
#     if ( -l www_image_50pct )
#             unlink(www_image_50pct) or die "Can't unlink www_image_50pct: !\n"
#
#     symlink(output_50pct, www_image_50pct) or die "Can't symlink output_50pct to www_image_50pct: !\n"
#     if ( -l www_image_orig )
#             unlink(www_image_orig) or die "Can't unlink www_image_orig: !\n"
#
#     symlink(output_orig, www_image_orig) or die "Can't symlink output_orig to www_image_orig: !\n"
#     if ( -l www_public_image_50pct )
#             unlink(www_public_image_50pct) or die "Can't unlink www_public_image_50pct: !\n"
#
#     symlink(public_output_50pct, www_public_image_50pct) or die "Can't symlink public_output_50pct to www_public_image_50pct: !\n"
#     if ( -l www_public_image_orig )
#             unlink(www_public_image_orig) or die "Can't unlink www_public_image_orig: !\n"
#
#     symlink(public_output_orig, www_public_image_orig) or die "Can't symlink public_output_orig to www_public_image_orig: !\n"
#
#     stash_dir = sc6_general.get_image_dir(self.dt, "stash", self.mode)
#     noon_link = stash_dir, "/noon.jpg"
#     rise_link = stash_dir, "/sunrise.jpg"
#     set_link = stash_dir, "/sunset.jpg"
#     if ( ! -l noon_link )
#         if ( self.->is_after_noon(self.dt) )
#             print "gonna link output_orig to noon_link\n";# do link stuff
#             symlink(output_orig, noon_link) or die "Can't link output_orig to noon_link: !\n"
#
#
#     if ( ! -l rise_link )
#         if ( self.->is_afterrise(self.dt) )
#             print "gonna link output_orig to rise_link\n";# do link stuff
#             symlink(output_orig, rise_link) or die "Can't link output_orig to rise_link: !\n"
#
#
#     if ( ! -l set_link )
#         if ( self.->is_afterset(self.dt) )
#             print "gonna link output_orig to set_link\n";# do link stuff
#             symlink(output_orig, set_link) or die "Can't link output_orig to set_link: !\n"
#
#
#
#
#
    def getBluecode(self):
        if not self.bc:
            self.bc = sc6_bluecode(self.output)
        return(self.bc.bluecode)

# sub getBluecodes
#     my (self) = @_
#
#     if ( ! self.bc )
#         self.bc = new SC6::Cam::BlueCode(self.output_50pct)
#
#     return( (self.bc']['_r, self.bc']['_g, self.bc']['_b, self.bc']['_x, self.bc']['_lum) )
#
#
#
#
# sub getOutputFile
#     my (self) = @_
#
#     return( self.output )
#
#
# sub getPublicMask
#     my (self) = @_
#
#     return ( self.public_mask )
#
#
# sub getHour
#     my (self) = @_
#
#     return( self.dt->hour )
#
#
# sub getMinute
#     my (self) = @_
#
#     return( self.dt->minute )
#
#
# sub make_public_version
#     my ( self ) = @_
#     SC6::Cam::Overlay::do_public_version(self)
#
#
# sub do_image_overlays
#     my ( self ) = @_
#     SC6::Cam::Overlay::do_overlays(self)
#
#
# sub i_do_cmd
#     my (self, cmd) = @_
#     print cmd, "\n"
#     if ( ! self.dryrun )
#         print `cmd`
# #        print `cmd 2>&1`
#
#     return ?
#
#

    def print_my_dirs(self):

        print("self.output:\t\t", self.output)
        print("self.output_50pct:\t", self.output_50pct)

        # public version of image (with mask) saved for one day
        print("self.public_output:\t\t", self.public_output)
        print("self.public_output_50pct:\t", self.public_output_50pct)

        print("self.www_image_orig:\t\t", self.www_image_orig)
        print("self.www_image_50pct:\t\t", self.www_image_50pct)
        print("self.www_public_image_orig:\t", self.www_public_image_orig)
        print("self.www_public_image_50pct:\t", self.www_public_image_50pct)


if __name__ == '__main__':

    iset = ImageSet()
    iset.print_my_dirs()
    iset.fetch()
