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
        self.logger = logging.getLogger(__name__)

        self.config_file = config_file
        self.mode = mode

        # make sure we hav a config file
        if not self.config_file or not os.path.exists(self.config_file):
            print("Config file {} does not exist".format(self.config_file))
            sys.exit(1)

        self.logger.debug("config file is {}".format(self.config_file))
        with open(self.config_file, 'r') as file:
            self.config_root = yaml.safe_load(file)
        try:
            self.config = self.config_root[self.mode]
        except KeyError:
            print("mode config wrong, should be something like \
                'prod' or 'test', is {}".format(self.mode))
            sys.exit(1)
        self.logger.debug("config for {} loaded".format(self.mode))

        try:
            self.debug = self.config['Debug']['Level']
        except (KeyError, TypeError):
            self.debug = 0
        try:
            dumpconfig = self.config['Debug']['DumpConfig']
        except (KeyError, TypeError):
            dumpconfig = 99

        # see if this config tree is templated upon another
        # There is no further recursion of templates
        try:
            template = self.config['Config']['Template']
        except KeyError:
            pass
        else:
            try:
                self.logger.debug("going to load template {}".format(template))
                tmpl_config = self.config_root[template]
            except KeyError:
                print("template config wrong, should name of another config \
                    root, is {}".format(template))
                sys.exit(1)
            else:
                out = self.merge(self.config, tmpl_config)
                self.config = out

        try:
            self.debug = self.config['Debug']['Level']
        except (KeyError, TypeError):
            self.debug = 0
        try:
            dumpconfig = self.config['Debug']['DumpConfig']
        except (KeyError, TypeError):
            dumpconfig = 99

        if self.debug >= dumpconfig:
            self.logger.debug(self.config)

    def merge(self, a, b, path=None):
        "merges b into a"
        if path is None:
            path = []
        for key in b:
            if key in a:
                if isinstance(a[key], dict) and isinstance(b[key], dict):
                    self.merge(a[key], b[key], path + [str(key)])
                elif a[key] == b[key]:
                    pass  # same leaf value
                else:
                    pass  # keep the a value
            else:
                a[key] = b[key]
        return a

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

    print("mode = test")
    config_test = Config(mode='test')
    config = config_test.get_config()
#    pprint.pprint(config)
    print("['Directories']['cam_images']['prod']:",
          config['Directories']['cam_images']['prod'])
    print("['Paths']['cam_images']:",
          config['Paths']['cam_images'])
    print("config['BucketShiz']['VideoNameTemplate']",
          config['BucketShiz']['VideoNameTemplate'])

    print("mode = prod")
    config_prod = Config(mode='prod')
    config = config_prod.get_config()
#    pprint.pprint(config)
    print("['Directories']['cam_images']['prod']:",
          config['Directories']['cam_images']['prod'])
    print("['Paths']['cam_images']:",
          config['Paths']['cam_images'])
    print("config['BucketShiz']['VideoNameTemplate']",
          config['BucketShiz']['VideoNameTemplate'])

    print("mode = shiz")
    config_shiz = Config(mode='shiz')
    config = config_shiz.get_config()
    print("['Directories']['cam_images']['prod']:",
          config['Directories']['cam_images']['prod'])
    print("['Paths']['cam_images']:",
          config['Paths']['cam_images'])
    print("config['BucketShiz']['VideoNameTemplate']",
          config['BucketShiz']['VideoNameTemplate'])
