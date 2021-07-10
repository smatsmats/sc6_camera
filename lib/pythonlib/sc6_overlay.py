#!/usr/bin/python3

# TODO
# add clock and other optional overlays
# make mode work right

import argparse
import os
import sys
import logging
import logging.config
# import pprint
import yaml
from PIL import Image, ImageColor, ImageDraw
from stat import *
from math import pi, sin, cos

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_sun
import sc6_general
import sc6_image
import sc6_bluecode

# use DateTime
# use GD
# use GD::Graph::hbars
# use SC6::Cam::WX
# use Graphics::ColorNames 2.10
# use Data::Dumper

# uses the image object

with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

#  create logger
logger = logging.getLogger('SC6Overlay')


def do_public_version(imageset):

    if not config['Public']['Enable']:
        print("skipping do_public_version")
        return

    if imageset.debug:
        print("file: ", imageset.output)
    try:
        main = Image.open(imageset.output)
    except FileNotFoundError:
        print("file {} missing, need an image ".format(imageset.output))
        os.exit()
    except:
        print("Can't process image file: {}".format(imageset.output))
        os.exit()

    mask = imageset.public_mask

    # add the alpha channel to jpg
    main_rgba = main.convert(mode="RGBA")
    # overlay the mask
    main_rgba.alpha_composite(im=mask)

    # saving the object into the current image obj as only rgb
    imageset.public_version = main_rgba.convert(mode="RGB")

    # now write that out
    write_public_version(imageset)


def write_current_version(imageset):
    image_file = imageset.output
    try:
        imageset.current.save(image_file)
    except OSError as error:
        print("Can't write file {} error: {}".format(image_file, error))


def write_public_version(imageset):
    public_image_file = imageset.public_output
    try:
        imageset.public_version.save(public_image_file)
    except OSError as error:
        print("Can't write file {} error: {}".format(public_image_file, error))


def do_overlays(imageset):

    if not config['Overlay']['Clock']['Overlay'] and \
       not config['Overlay']['ColorGraph']['Overlay'] and \
       not config['Overlay']['WX']['Overlay']:
        return

    # copy current image as RGBA to work on it
    main = imageset.current.convert(mode="RGBA")
    # also do overlays to public version
    public = imageset.public_version.convert(mode="RGBA")

    minute = imageset.dt.minute
    hour = imageset.dt.hour

    bluecode = imageset.getBluecode()
    bc_set = imageset.getBluecodes()
#    my (r, g, b, x, lum) = imageset.getBluecodes()
    mysun = sc6_sun.SC6Sun()

    # get the clock
    if config['Overlay']['Clock']['Overlay']:
        clock_overlay = add_clock(hour, minute)
        cw = clock_overlay.width
        ch = clock_overlay.height
        clock_xy = overlay_location("Clock", main.width, main.height, cw, cw)
        if imageset.debug:
            print("Copy clock to coordinates: {} {}".format(clock_xy[0],
                                                            clock_xy[1]))
        main.alpha_composite(im=clock_overlay, dest=clock_xy)
        public.alpha_composite(im=clock_overlay, dest=clock_xy)

    # get the colorGraph of bluecode
    # if we ever want to do this again make this like the clock code above
#     if ( lc(config['Overlay']['ColorGraph]['Overlay']) eq "true" ) {
#         cg_overlay = add_colorgraph(r, g, b, x, bluecode, lum)
#         my (cgw,cgh) = cg_overlay.getBounds()
#         my (cg_x, cg_y) = 
#             overlay_location("ColorGraph", main.width, main.height, cgw, cgh)
#         print("Copy ColorGraph to coordinates: cg_x,cg_y\n"
#         if ( main::debug )
#         main.copy(cg_overlay,cg_x,cg_y,0,0,cgw,cgh)
#         public.copy(cg_overlay,cg_x,cg_y,0,0,cgw,cgh)

    # get the WX graphs
    # if we ever want to do this again make this like the clock code above
#     if ( lc(config['Overlay']['WX]['Overlay']) eq "true" ) {
#         overlay = add_wx_overlays(s, w, h)
#         my (o_w,o_h) = overlay.getBounds()
#         my (o_x, o_y) = overlay_location("WX", main.width, main.height, o_w, o_h)
#         # a instead of doing an overlay create a new image with the graphs appended
#         new_main = GD::Image.new(main.width, main.height + o_h, 1)
#         new_main.copy(main,0,0,0,0,main.width,main.height)
#         print("Appending WX Graphs\n" if ( main::debug )
#         new_main.copy(overlay,0,h,0,0,o_w,o_h)
#         main = new_main

    # copy back main / current image as RGB
    imageset.current = main.convert(mode="RGB")
    write_public_version(imageset)
    write_current_version(imageset)


def add_clock(hour, minute):

    width = config['Overlay']['Clock']['Width']
    height = config['Overlay']['Clock']['Height']
    x_border = config['Overlay']['Clock']['XBorder']
    y_border = config['Overlay']['Clock']['YBorder']

    # center
    cx = width / 2
    cy = height / 2

    # thickness
    thickness = config['Overlay']['Clock']['LineWeight']

    im = Image.new(mode="RGBA",
                   size=(width, height),
                   color=(255, 255, 255, 0))

    # get colors
    fg_color = ImageColor.getrgb(config['Overlay']['Clock']['FGColor'])
    bg_color = ImageColor.getrgb(config['Overlay']['Clock']['BGColor'])

    # radiuses
    hradius = width / 4
    mradius = (width / 2) * .70

    draw = ImageDraw.Draw(im)
#
#     # Create a brush with a round end
#     round_brush = new GD::Image(t*2,t*2)
#     # first color allocated is background color
#     rb_bg_color = round_brush.colorAllocate(@bg_color)
#     rb_fg_color = round_brush.colorAllocate(@fg_color)
#     round_brush.transparent(rb_bg_color)
#
    # draw the circle
    draw.arc(xy=[(0, 0), (width, height)],
             start=0,
             end=360,
             fill=fg_color,
             width=thickness)
#
#     # if you need to see the brush, uncomment this
#     #im.copy(round_brush,0,0,0,0,t*2,t*2)
#
#     # Set the brush
#     im.setBrush(round_brush)
#
#     # maybe antialiased
#     im.setAntiAliased(im_fg_color)
#
#     # cicle
#     im.arc(cx,cy,width - t*2 - x_border,height - t*2 -
#         y_border,0,360,gdAntiAliased)
#
    # minute hand
    minute_xy = minute_point(minute, cx, cy, mradius)
    draw.line(xy=[(cx, cy), minute_xy], fill=fg_color, width=thickness)

    # hour hand
    hour_xy = hour_point(hour, minute, cx, cy, hradius)
    draw.line(xy=[(cx, cy), hour_xy], fill=fg_color, width=thickness)

    if config['Overlay']['Clock']['WriteImage']:
        file = config['Overlay']['Clock']['ImageFile']
        try:
            im.save(file)
        except OSError as error:
            print("Can't write file {} error: {}".format(file, error))

    return(im)

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


def minute_point(minute, xcenter, ycenter, mradius):

    x = xcenter + (mradius*(sin(2*pi*(minute/60))))
    y = ycenter + (-1*mradius*(cos(2*pi*(minute/60))))

    return((x, y))


def hour_point(hour, minute, xcenter, ycenter, hradius):

    totalSeconds = (3600*hour + 60*minute) / 43200
    x = xcenter + (hradius*(sin(2*pi*totalSeconds)))
    y = ycenter + (-1*hradius*(cos(2*pi*totalSeconds)))

    return((x, y))


def overlay_location(otype, main_x, main_y, ox, oy):

    # configuration location of ColorGraph
    config_x = config['Overlay'][otype]['XLocation']
    config_y = config['Overlay'][otype]['YLocation']

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

    iset = sc6_image.ImageSet()
    iset.print_my_dirs()
    iset.fetch()
    iset.getBluecode()
    iset.make_public_version()
    iset.do_image_overlays()
