#!/usr/bin/python3

import argparse
import os
import sys
import logging
import logging.config
import yaml
from PIL import Image, ImageColor, ImageDraw
from stat import *
from math import pi, sin, cos

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_sun
import sc6_general
import sc6_image
import sc6_bluecode

with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

#  create logger
logger = logging.getLogger('SC6Overlay')


def get_clock(dt):

    width = config['Overlay']['Clock']['Width']
    height = config['Overlay']['Clock']['Height']
    # thickness
    thickness = config['Overlay']['Clock']['LineWeight']

    im = Image.new(mode="RGBA",
                   size=(width, height),
                   color=(255, 255, 255, 0))

    # adjust circle width to fit all of pen thickness
    width = width - (thickness / 2)
    height = height - (thickness / 2)

    # center
    cx = width / 2
    cy = height / 2

    # get colors
    fg_color = ImageColor.getrgb(config['Overlay']['Clock']['FGColor'])
    bg_color = ImageColor.getrgb(config['Overlay']['Clock']['BGColor'])

    # radiuses
    hradius = width / 4
    mradius = (width / 2) * .70

    draw = ImageDraw.Draw(im)

    # draw the circle
    draw.arc(xy=[(0, 0), (width, height)],
             start=0,
             end=360,
             fill=fg_color,
             width=thickness)

    # minute hand
    minute_xy = minute_point(dt.minute, cx, cy, mradius)
    draw.line(xy=[(cx, cy), minute_xy], fill=fg_color, width=thickness)

    # hour hand
    hour_xy = hour_point(dt.hour, dt.minute, cx, cy, hradius)
    draw.line(xy=[(cx, cy), hour_xy], fill=fg_color, width=thickness)

    if config['Overlay']['Clock']['WriteImage']:
        file = config['Overlay']['Clock']['ImageFile']
        try:
            im.save(file)
        except OSError as error:
            print("Can't write file {} error: {}".format(file, error))

    return(im)

# still psuedo-perl code, not yet converted to python, maybe never needs to be
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
# #    graph.set( dclrs => [ qw(config['Overlay']['ColorGraph]['FGColor]
#             config['Overlay']['ColorGraph]['LumColor] red green blue
#             config['Overlay']['ColorGraph]['XColor]) ] )
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
#     if ( main::debug ):
#         print("length of day: length_day, so far day_so_far, ",
#             (day_so_far / length_day * 100), "% of the way there\n"
#     rrd_width = width * (day_so_far / length_day)
#
#     rrdtool = config['WX]['rrdtool]
#     outfile = config['WX]['attr]['ImageFile]
#     title = "\"" . attr . "\""
#     vlabel = "\"" . config['WX]['attr]['VLabel] . "\""
#     dd = config['WX]['attr]['DD]
#     rrd_args = config['WX]['attr]['RRDOtherArgs]
#
#     cmd = "rrdtool graph outfile --no-legend --full-size-mode
#       --units-exponent
#       0 -E -a PNG --alt-y-grid -v vlabel -w rrd_width -h height
#       -s -day_so_far rrd_args dd"
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
