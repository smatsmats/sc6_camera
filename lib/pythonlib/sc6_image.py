#!/usr/bin/python3

import argparse
import os
import sys
import logging
import logging.config
# import pprint
import yaml
from stat import *
from PIL import Image, ImageColor, ImageDraw, UnidentifiedImageError
from math import pi, sin, cos

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_sun
import sc6_general
import sc6_image
import sc6_bluecode
import sc6_overlay
import sc6_config


class ImageSet:
    def __init__(self, debug=False, config=None):

        if config is None:
            mode = "prod"
            cfg = sc6_config.Config(mode=mode)
            config = cfg.get_config()

#        self.fn = fn
        self.debug = debug or config['Debug']
        self.config = config

        with open(config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)

        #  create logger
        self.logger = logging.getLogger('SC6Image')
        self.logger.setLevel(logging.DEBUG)

#        if self.debug:
#            handler = logging.StreamHandler(sys.stdout)
#            handler.setLevel(logging.DEBUG)
#            formatter = logging.Formatter(
#                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#            handler.setFormatter(formatter)
#            self.logger.addHandler(handler)

        self.mysun = sc6_sun.SC6Sun()
        self.dt = self.mysun.get_dt()
        self.dt_epoch = self.mysun.dt_epoch

        # size isn't really used yet, so we just set it staticallyk
        self.size = "orig"
        # set this somewhere else
        self.mode = "prod"

        # these are the files that are saved
        image_dir = sc6_general.get_image_dir(self.dt, "orig", self.mode)
        self.output = "{}image{}_orig.jpg".format(image_dir, self.dt_epoch)
        image_dir = sc6_general.get_image_dir(self.dt, "50pct", self.mode)
        self.output_50pct = \
            "{}image{}_50pct.jpg".format(image_dir, self.dt_epoch)

        # public version of image (with mask) for video
        public_image_dir = \
            sc6_general.get_image_dir(self.dt, "public", self.mode)
        self.public_output = \
            "{}image{}_orig.jpg".format(public_image_dir, self.dt_epoch)
        public_image_dir = \
            sc6_general.get_image_dir(self.dt, "public_50pct", self.mode)
        self.public_output_50pct = \
            "{}image{}_50pct.jpg".format(public_image_dir, self.dt_epoch)

        # these are the files / links used on the web page
        www_dir = \
            sc6_general.get_www_dir(self.size, self.mode)
        www_public_dir = \
            sc6_general.get_www_public_dir(self.size, self.mode)
        self.www_image_orig = \
            os.path.join(www_dir, config['Image']['File']['orig'])
        self.www_image_50pct = \
            os.path.join(www_dir, config['Image']['File']['50pct'])
        self.www_public_image_orig = \
            os.path.join(www_public_dir, config['Image']['File']['orig'])
        self.www_public_image_50pct = \
            os.path.join(www_public_dir, config['Image']['File']['50pct'])

        self.public_mask = self.load_privacy_mask()

    def load_privacy_mask(self):
        if not self.config['Public']['Enable']:
            return None

        mask_file = self.config['Public']['MaskFile']
        try:
            mask_image = Image.open(mask_file)
        except FileNotFoundError:
            print("file {} missing, need a ['Public']['MaskFile']".format(
                 mask_file))
            sys.exit()
        except:
            print("Can't process mask file: {}".format(mask_file))
            sys.exit()
        return mask_image

    def fetch(self):

        command = self.config['Image']['Fetch']['Command']
        args = self.config['Image']['Fetch']['ArgsList']

        cmd = [command]
        cmd = cmd + args
        cmd.append(self.output)

        ret = sc6_general.run_cmd(cmd, self.debug)

        self.success = 0
        if ret == 0 and os.path.exists(self.output):
            size = os.path.getsize(self.output)
            if size >= self.config['Image']['MinSize']:
                self.success = 1
                # now open the image and store the object
                try:
                    self.current = Image.open(self.output)
                except FileNotFoundError:
                    print("file {} missing, need an image".format(self.output))
                    sys.exit()
                except UnidentifiedImageError:
                    print("UnidentifiedImageError {}".format(self.output))
                    sys.exit()
                except:
                    print("Can't process current file: {}".format(self.output))
                    sys.exit()
            else:
                try:
                    os.unlink(self.output)
                except OSError:
                    print("return code is not 0 ret or file is too small")
                    pass

        return self.success

    def resizes_and_links(self):

        half_width = int(self.current.width / 2)
        half_height = int(self.current.height / 2)

        # resizes
        image_output_50pct = self.current.resize((half_width, half_height))
        self.write_image(image_output_50pct, self.output_50pct)
        image_public_50pct = self.public.resize((half_width, half_height))
        self.write_image(image_public_50pct, self.public_output_50pct)

        # this could be more friendly but I don't really care about it
        try:
            os.unlink(self.www_image_50pct)
            os.symlink(self.output_50pct, self.www_image_50pct)
        except OSError as error:
            self.logger.debug("{} {}".format(self.www_image_50pct, error))

        try:
            os.unlink(self.www_image_orig)
            os.symlink(self.output, self.www_image_orig)
        except OSError as error:
            self.logger.debug("{} {}".format(self.www_image_orig, error))

        try:
            os.unlink(self.www_public_image_50pct)
            os.symlink(self.public_output_50pct, self.www_public_image_50pct)
        except OSError as error:
            self.logger.debug("{} {}".format(self.www_public_image_50pct, error))

        try:
            os.unlink(self.www_public_image_orig)
            os.symlink(self.public_output, self.www_public_image_orig)
        except OSError as error:
            self.logger.debug("{} {}".format(self.www_public_image_orig, error))

        stash_dir = sc6_general.get_image_dir(self.dt, "stash", self.mode)
        noon_link = os.path.join(stash_dir, "noon.jpg")
        rise_link = os.path.join(stash_dir, "sunrise.jpg")
        set_link = os.path.join(stash_dir, "sunset.jpg")

        if not os.path.exists(noon_link):
            if self.mysun.is_after_noon():
                print("gonna link {} to {}".format(self.output, noon_link))
                try:
                    os.symlink(self.output, noon_link)
                except OSError as error:
                    self.logger.debug("{} {}".format(noon_link, error))

        if not os.path.exists(rise_link):
            if self.mysun.is_afterrise():
                print("gonna link {} to {}".format(self.output, rise_link))
                try:
                    os.symlink(self.output, rise_link)
                except OSError as error:
                    self.logger.debug("{} {}".format(rise_link, error))

        if not os.path.exists(set_link):
            if self.mysun.is_after_sunset():
                print("gonna link {} to {}".format(self.output, set_link))
                try:
                    os.symlink(self.output, set_link)
                except OSError as error:
                    self.logger.debug("{} {}".format(set_link, error))

    def getBluecode(self):
        try:
            self.bc
        except AttributeError:
            self.bc = sc6_bluecode.BlueCode(fn=self.output, 
                                            debug=self.debug, 
                                            config=self.config)

        return(self.bc.bluecode)

    def getBluecodes(self):
        self.getBluecode()
        bc_set = {'r': self.bc.r,
                  'g': self.bc.g,
                  'b': self.bc.b,
                  'x': self.bc.x,
                  'lum': self.bc.lum}
        return(bc_set)

    def write_image(self, im, filename):
        try:
            im.save(filename)
        except OSError as error:
            print("Can't write file {} error: {}".format(filename, error))

    def write_current_version(self):
        self.write_image(self.current, self.output)

    def write_public_version(self):
        self.write_image(self.public, self.public_output)

    def make_public_version(self):
        self.write_image(self.current, self.output)

        if not self.config['Public']['Enable']:
            self.logger.debug("skipping do_public")
            return

        mask = self.public_mask

        # add the alpha channel to jpg
        main_rgba = self.current.convert(mode="RGBA")
        # overlay the mask
        main_rgba.alpha_composite(im=mask)

        # saving the object into the current image obj as only rgb
        self.public = main_rgba.convert(mode="RGB")

        # now write that out
        self.write_public_version()

    def do_image_overlays(self):

        if not self.config['Overlay']['Clock']['Overlay'] and \
           not self.config['Overlay']['ColorGraph']['Overlay'] and \
           not self.config['Overlay']['WX']['Overlay']:
            return

        # copy current image as RGBA to work on it
        main = self.current.convert(mode="RGBA")
        # also do overlays to public version
        public = self.public.convert(mode="RGBA")

        bluecode = self.getBluecode()
        bc_set = self.getBluecodes()
#    my (r, g, b, x, lum) = self.getBluecodes()

        # do we need this?
        # mysun = sc6_sun.SC6Sun()

        # get the clock
        if self.config['Overlay']['Clock']['Overlay']:
            clock_overlay = sc6_overlay.get_clock(self.dt)
            cw = clock_overlay.width
            ch = clock_overlay.height
            clock_xy = self.overlay_location("Clock", main.width,
                                             main.height, cw, cw)
            if self.debug:
                self.logger.debug("Copy clock to coordinates: {} {}".format(
                                                                clock_xy[0],
                                                                clock_xy[1]))
            main.alpha_composite(im=clock_overlay, dest=clock_xy)
            public.alpha_composite(im=clock_overlay, dest=clock_xy)

    # get the colorGraph of bluecode
    # if we ever want to do this again make this like the clock code above
#     if ( lc(config['Overlay']['ColorGraph]['Overlay']) eq "true" ) {
#         cg_overlay = add_colorgraph(r, g, b, x, bluecode, lum)
#         my (cgw,cgh) = cg_overlay.getBounds()
#         my (cg_x, cg_y) =
#             self.overlay_location("ColorGraph", main.width,
# main.height, cgw, cgh)
#         print("Copy ColorGraph to coordinates: cg_x,cg_y\n"
#         if ( main::debug )
#         main.copy(cg_overlay,cg_x,cg_y,0,0,cgw,cgh)
#         public.copy(cg_overlay,cg_x,cg_y,0,0,cgw,cgh)

    # get the WX graphs
    # if we ever want to do this again make this like the clock code above
#     if ( lc(config['Overlay']['WX]['Overlay']) eq "true" ) {
#         overlay = add_wx_overlays(s, w, h)
#         my (o_w,o_h) = overlay.getBounds()
#         my (o_x, o_y) = self.overlay_location("WX", main.width, main.height, o_w, o_h)
#         # a instead of doing an overlay create a new image with the graphs appended
#         new_main = GD::Image.new(main.width, main.height + o_h, 1)
#         new_main.copy(main,0,0,0,0,main.width,main.height)
#         print("Appending WX Graphs\n" if ( main::debug )
#         new_main.copy(overlay,0,h,0,0,o_w,o_h)
#         main = new_main

        # copy back main / current image as RGB
        self.current = main.convert(mode="RGB")
        self.write_public_version()
        self.write_current_version()

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

    def overlay_location(self, otype, main_x, main_y, ox, oy):

        # configuration location of ColorGraph
        config_x = self.config['Overlay'][otype]['XLocation']
        config_y = self.config['Overlay'][otype]['YLocation']

        # translate natural language config options
        if config_x == "left":
            config_x = 0
        if config_x == "right":
            config_x = 100
        if config_y == "top":
            config_y = 0
        if config_y == "bottom":
            config_y = 100

        # image location
        x = (main_x - ox) * config_x / 100
        y = (main_y - oy) * config_y / 100

#    return {'x': x, 'y': y}
        return ((int(x), int(y)))

# ######################3 overlay code





# sub add_wx_overlays {
#     my (s, main_w, main_h) = @_
#
#     wx = SC6::Cam::WX.new()
#     print("rain today: ", wx.rain_today, "")
#
#     indi_width = config['Overlay']['WX]['IndividualWidth]
#     indi_height = config['Overlay']['WX]['IndividualHeight]
#
#     my @graphs_maybe = ( "TDW", "Rain", "Pressure", "Wsp", "Dir", "Solar")
#     my @graphs
#     foreach g ( @graphs_maybe ) {
# #        next if ( g eq "Rain" && wx.rain_today == 0 )
#         push @graphs, wx_graph(g, s, indi_width, indi_height)
#     ]
#
#     im = new GD::Image(indi_width,indi_height * (#graphs+1))
#     # allocate some colors
#     white = im.colorAllocate(255,255,255)
#     black = im.colorAllocate(0,0,0)
#     # make the background transparent and interlaced
#     im.transparent(white)
#
#     upper_left_x = 0
#     foreach o ( @graphs ) {
#         im.copy(o,0,upper_left_x,0,0,indi_width,indi_height)
#         upper_left_x += indi_height
#     ]
#
#     if ( lc(config['Overlay']['WX]['WriteImage]) eq "true" ) {
#         file = config['Overlay']['WX]['ImageFile]
#         open OUT, ">file" or die "Can't open file for writing: !")
#         binmode OUT
#         print(OUT im.jpeg
#         close OUT
#     ]
#
#     return(im)
# ]
#
# sub add_colorgraph {
#     my (r, g, b, x, bluecode, lum) = @_
#
#     my @data = (
#         ["BC","Lum","R","G","B","X"],
#         [bluecode, lum, r, g, b, x]
#     )
#     width = config['Overlay']['ColorGraph]['Width]
#     height = config['Overlay']['ColorGraph]['Height]
#     x_border = config['Overlay']['ColorGraph]['XBorder]
#     y_border = config['Overlay']['ColorGraph]['YBorder]
#
#     # center
#     cx = width / 2
#     cy = height / 2
#
#     # thickness
#     t = config['Overlay']['ColorGraph]['LineWeight]
#
#     graph = GD::Graph::hbars.new(width,height)
#
# #    graph.set( dclrs => [ qw(config['Overlay']['ColorGraph]['FGColor] config['Overlay']['ColorGraph]['LumColor] red green blue config['Overlay']['ColorGraph]['XColor]) ] )
#     graph.set( dclrs => [ qw(pink yellow red green blue white) ])
#     graph.set(
#       cycle_clrs           => 1,
#       y_min_value       => 0,
#       show_values       => 1,
#       values_format       => "%d",
#     ) or die graph.error
#     im = graph.plot(\@data)
#
#     if ( lc(config['Overlay']['ColorGraph]['WriteImage]) eq "true" ) {
#         file = config['Overlay']['ColorGraph]['ImageFile]
#         open OUT, ">file" or die "Can't open file for writing: !")
#         binmode OUT
#         print(OUT im.jpeg
#         close OUT
#     ]
#
#     return(im)
# ]
#

def wx_graph(attr, s, width, height):
    return()
#
#     # get time ranges and image size
#     length_day = s['naut_dusk].epoch() - s['naut_dawn].epoch()
#     dt = DateTime.now(  time_zone => config[''General'][''Timezone'] )
#     day_so_far = dt.epoch() - s['naut_dawn].epoch()
#     print("length of day: length_day, so far day_so_far, ", (day_so_far / length_day * 100), "% of the way there\n" if ( main::debug )
#     rrd_width = width * (day_so_far / length_day)
#
#     rrdtool = config['WX]['rrdtool]
#     outfile = config['WX]['attr]['ImageFile]
#     title = "\"" . attr . "\""
#     vlabel = "\"" . config['WX]['attr]['VLabel] . "\""
#     dd = config['WX]['attr]['DD]
#     rrd_args = config['WX]['attr]['RRDOtherArgs]
#
#     cmd = "rrdtool graph outfile --no-legend --full-size-mode --units-exponent 0 -E -a PNG --alt-y-grid -v vlabel -w rrd_width -h height -s -day_so_far rrd_args dd"
#     print(cmd, "\n" if ( main::debug )
#     print(`cmd`
#
#     # create a new full sized image
#     im = new GD::Image(width,height)
#     # allocate some colors
#     white = im.colorAllocate(255,255,255)
#     black = im.colorAllocate(0,0,0);
#     # make the background transparent and interlaced
#     im.transparent(white)
#
#     # read back in the rrd graph and copy
#     rrd_im = GD::Image.newFromPng(outfile)
#     im.copy(rrd_im,0,0,0,0,rrd_width,height)
#
#     return im;


if __name__ == '__main__':

    iset = ImageSet()
    iset.print_my_dirs()
    iset.fetch()
    iset.getBluecode()
    iset.make_public_version()
    iset.do_image_overlays()
    iset.resizes_and_links()
