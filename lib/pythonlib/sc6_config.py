#!/usr/bin/python3

# use YAML
# use YAML::Tiny
# use Data::Dumper
# use Hash::Merge::Simple qw/ merge /

import argparse
import os
import sys
import logging
import logging.config
import pprint
import yaml


class Config:
    def __init__(self,
                 config_file='/usr/local/cam/conf/config.yml',
                 mode='prod'):

        # start with a temporty config to get things started
        with open('/usr/local/cam/conf/config.yml', 'r') as file:
            config_root = yaml.safe_load(file)
        config = config_root['prod']

        with open(config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)

        #  create logger
        self.logger = logging.getLogger('SC6Config')

        self.config_file = config_file
        self.mode = mode

        # make sure we hav a config file
        if not self.config_file or not os.path.exists(self.config_file):
            print("Config file {} does not exist".format(self.config_file))
            sys.exit(1)

        with open(self.config_file, 'r') as file:
            self.config_root = yaml.safe_load(file)
        try:
            self.config = self.config_root[self.mode]
        except KeyError:
            print("mode config wrong, should be something like \
                'prod' or 'test', is {}".format(self.mode))
            sys.exit(1)

        # see if this config tree is templated upon another
        # There is no further recursion of templates
        try:
            template = self.config['Config']['Template']
        except KeyError:
            pass
        else:
            try:
                tmpl_config = self.config_root[template]
            except KeyError:
                print("template config wrong, should name of another config \
                    root, is {}".format(template))
                sys.exit(1)
            else:
                self.config = tmpl_config.update(self.config)

        try:
            self.debug = self.config['Debug']['Level']
        except (KeyError, TypeError):
            self.debug = 0
        try:
            dumpconfig = self.config['Debug']['DumpConfig']
        except (KeyError, TypeError):
            dumpconfig = 99

        if self.debug >= dumpconfig:
            print("merged config:")
            pprint.pprint(self.config)

    def get_config(self):
        return(self.config)

# never implemented, never used
# sub writeConfig {
#     my (self, $old ) = @_
#
#     # replace config
#     self.in}->[0]->{prod} = $old
#     if ( self.debug} >= self.config]['Debug']['DumpConfig'} ) {
#         print("going to write:", Dumper(self.in})
#     # write new config
#     if ( ! self.in}->write( self.config_file} ) ) {
#         die "errors writing ", self.config_file}, " : $!\n"


if __name__ == '__main__':

    config = Config()
    config = Config(mode='test')
    print("['Directories']['cam_images']['prod']:", config['Directories']['cam_images']['prod']
    print("['Paths']['cam_images']:", config['Paths']['cam_images']
    config = Config(mode='prod')
    print("['Directories']['cam_images']['prod']:", config['Directories']['cam_images']['prod']
    print("['Paths']['cam_images']:", config['Paths']['cam_images']
    config = Config(mode='shiz')
    print("['Directories']['cam_images']['prod']:", config['Directories']['cam_images']['prod']
    print("['Paths']['cam_images']:", config['Paths']['cam_images']
