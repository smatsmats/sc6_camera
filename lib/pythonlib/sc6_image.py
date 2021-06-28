#!/usr/bin/python3

# from datetime import datetime
# from datetime import timedelta
# import pytz
# import astral
# from astral import LocationInfo
# from astral.sun import sun

import argparse
import sys
import logging
import logging.config
# import pprint
import yaml
#
# use SC6::Cam::General
# use SC6::Cam::BlueCode
# use SC6::Cam::Overlay
# use SC6::Cam::GStore
#

sys.path.append('/usr/local/cam/lib/pythonlib')
#import bucket_shiz
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
#        dt
#        mode
#        dryrun
#        sun

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

#        # these are the files / links used on the web page
#        www_dir = get_www_dir(size, self.mode)
#        www_public_dir = get_www_public_dir(size, self.mode)
#        self.www_image_orig = www_dir . main::config->{Image->{File->{orig
#        self.www_image_50pct = www_dir . main::config->{Image->{File->{'50pct'
#        self.www_public_image_orig = www_public_dir . main::config->{Image->{File->{orig
#        self.www_public_image_50pct = www_public_dir . main::config->{Image->{File->{'50pct'

#     self.public_mask = load_privacy_mask()
#
#     bless self, class
#     return self
# 
#
# sub load_privacy_mask {
#     if ( lc(main::config->{Public->{Enable) ne "true" ) {
#         return undef
#     
#
#     mask_file = main::config->{Public->{MaskFile
#     mask_image = GD::Image->newFromPng(mask_file, 1)
#     if ( ! mask_image ) {
#         die "Can't make an image from mask_file\n"
#     
#     return mask_image
# 
#
# sub fetch {
#     my (self) = @_
#
#     first_args = main::config->{Image->{Fetch->{FirstArgs
#     middle_args = main::config->{Image->{Fetch->{MiddleArgs
#     final_args = main::config->{Image->{Fetch->{FinalArgs
#     extra_debug = main::config->{Image->{Fetch->{ExtraDebug
#     cmd = main::config->{Image->{Fetch->{Command
#
#     output = self.output
#
#     fetch_cmd = "cmd extra_debug first_args middle_args final_args output"
#     ret = i_do_cmd(self, fetch_cmd)
#
#     self.success = 0
#     size = 0
#     if ( ret == 0 && -f output ) {
#         size = (stat(output))[7]
#         if ( size > main::config->{Image->{MinSize ) {
#             self.success = 1
#         
#     
#
#     if ( self.success == 0 ) {
#         unlink output; # done't complain if we can't unlink
#         print "return code is not zero: ret or file is too small, size: size\n"
#     
#
#     return self.success
#
# 
#
# sub resizes_and_links {
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
#     if ( -l www_image_50pct ) {
#             unlink(www_image_50pct) or die "Can't unlink www_image_50pct: !\n"
#     
#     symlink(output_50pct, www_image_50pct) or die "Can't symlink output_50pct to www_image_50pct: !\n"
#     if ( -l www_image_orig ) {
#             unlink(www_image_orig) or die "Can't unlink www_image_orig: !\n"
#     
#     symlink(output_orig, www_image_orig) or die "Can't symlink output_orig to www_image_orig: !\n"
#     if ( -l www_public_image_50pct ) {
#             unlink(www_public_image_50pct) or die "Can't unlink www_public_image_50pct: !\n"
#     
#     symlink(public_output_50pct, www_public_image_50pct) or die "Can't symlink public_output_50pct to www_public_image_50pct: !\n"
#     if ( -l www_public_image_orig ) {
#             unlink(www_public_image_orig) or die "Can't unlink www_public_image_orig: !\n"
#     
#     symlink(public_output_orig, www_public_image_orig) or die "Can't symlink public_output_orig to www_public_image_orig: !\n"
#
#     stash_dir = sc6_general.get_image_dir(self.dt, "stash", self.mode)
#     noon_link = stash_dir . "/noon.jpg"
#     rise_link = stash_dir . "/sunrise.jpg"
#     set_link = stash_dir . "/sunset.jpg"
#     if ( ! -l noon_link ) {
#         if ( self.->is_after_noon(self.dt) ) {
#             print "gonna link output_orig to noon_link\n";# do link stuff
#             symlink(output_orig, noon_link) or die "Can't link output_orig to noon_link: !\n"
#         
#     
#     if ( ! -l rise_link ) {
#         if ( self.->is_afterrise(self.dt) ) {
#             print "gonna link output_orig to rise_link\n";# do link stuff
#             symlink(output_orig, rise_link) or die "Can't link output_orig to rise_link: !\n"
#         
#     
#     if ( ! -l set_link ) {
#         if ( self.->is_afterset(self.dt) ) {
#             print "gonna link output_orig to set_link\n";# do link stuff
#             symlink(output_orig, set_link) or die "Can't link output_orig to set_link: !\n"
#         
#     
# 
#
# sub getSun {
#     my (self) = @_
#     
#     return(self.)
#
# 
#
# sub getBluecode {
#     my (self) = @_
#     
#     if ( ! self.bc ) {
#         self.bc = new SC6::Cam::BlueCode(self.output)
#     
#     return(self.bc->{_bluecode)
#
# 
#
# sub getBluecodes {
#     my (self) = @_
#     
#     if ( ! self.bc ) {
#         self.bc = new SC6::Cam::BlueCode(self.output_50pct)
#     
#     return( (self.bc->{_r, self.bc->{_g, self.bc->{_b, self.bc->{_x, self.bc->{_lum) )
#
# 
#
# sub getPublicOutputFile {
#     my (self) = @_
#     
#     return( self.public_output )
# 
#
# sub getPublicOutputFile_50pct {
#     my (self) = @_
#     
#     return( self.public_output_50pct )
# 
#
# sub getPublicVersion {
#     my (self) = @_
#     return self.public_version
# 
#
# sub setPublicVersion {
#     my (self, pub) = @_
#     self.public_version = pub
# 
#
# sub getPublicWWWFile {
#     my (self) = @_
#     
#     return( self.www_public_image_orig )
# 
#
# sub getPublicWWWFile_50pct {
#     my (self) = @_
#     
#     return( self.www_public_image_50pct )
# 
#
# sub getOutputFile {
#     my (self) = @_
#     
#     return( self.output )
# 
#
# sub getPublicMask {
#     my (self) = @_
#
#     return ( self.public_mask )
# 
#
# sub getHour {
#     my (self) = @_
#     
#     return( self.dt->hour )
# 
#
# sub getMinute {
#     my (self) = @_
#     
#     return( self.dt->minute )
# 
#
# sub make_public_version {
#     my ( self ) = @_
#     SC6::Cam::Overlay::do_public_version(self)
# 
#
# sub do_image_overlays {
#     my ( self ) = @_
#     SC6::Cam::Overlay::do_overlays(self)
# 
#
# sub i_do_cmd {
#     my (self, cmd) = @_
#     print cmd, "\n"
#     if ( ! self.dryrun ) {
#         print `cmd`
# #        print `cmd 2>&1`
#     
#     return ?
# 
#
    def print_my_dirs(self):
        print("self.output:\t\t", self.output)
        print("self.output_50pct:\t", self.output_50pct)

        # public version of image (with mask) saved for one day so we can make video
        print("self.public_output:\t\t", self.public_output)
        print("self.public_output_50pct:\t", self.public_output_50pct)

#     print("self.www_image_orig:\t", self.www_image_orig)
#     print("self.www_image_50pct:\t", self.www_image_50pct)
#     print("self.www_public_image_orig:\t", self.www_public_image_orig)
#     print("self.www_public_image_50pct:\t", self.www_public_image_50pct)
#
# 
#

if __name__ == '__main__':


    iset = ImageSet()
    iset.print_my_dirs()
