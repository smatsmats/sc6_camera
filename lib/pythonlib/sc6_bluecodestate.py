#!/usr/bin/python3

import os
import sys
import yaml
import logging
import logging.config
import pytz
from datetime import datetime

sys.path.append('/usr/local/cam/lib/pythonlib')
import sc6_config
import sc6_sun
import sc6_general
import sc6_image


class BCS:
    def __init__(self, debug=False, config=None, mode="prod"):

        if config is None:
            cfg = sc6_config.Config(mode=mode)
            config = cfg.get_config()

        self.debug = debug or config['Debug']
        self.config = config
        self.mode = mode

        with open(self.config['Logging']['LogConfig'], 'rt') as f:
            lconfig = yaml.safe_load(f.read())
        logging.config.dictConfig(lconfig)

        #  create logger
        self.logger = logging.getLogger('SC6BlueCodeState')
        self.logger.setLevel(logging.DEBUG)

        self.priming_bluecode = self.config['BlueCode']['PrimingValue']
        self.blue_code_file = self.config['BlueCode']['FullFilePath']
        self.tzname = self.config['General']['Timezone']

#        if self.debug:
#            handler = logging.StreamHandler(sys.stdout)
#            handler.setLevel(logging.DEBUG)
#            formatter = logging.Formatter(
#                '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#            handler.setFormatter(formatter)
#            self.logger.addHandler(handler)

        self.prime()

    def checkBluecode(self, imageset):

        new_bluecode = imageset.getBluecode()
#        current_bluecode = self.getConfirmedBluecode()
        current_bluecode = self.bluecode

        self.logger.debug("checking bluecode, new: {}  old: {}".format(new_bluecode, current_bluecode))
        if new_bluecode > current_bluecode:
            self.logger.debug("new bluecode, new: {} old: {}"\
               .format(new_bluecode, current_bluecode))
            self.bluecode = new_bluecode
            self.save_is_blueist_stash(imageset)
#            self.save_is_blueist_local(imageset.output)
            self.cache()
            return True

        return False

#    # not really sure what this does, leaving it for now
#    def getConfirmedBluecode(self):
#
#        unixtime = os.path.getmtime(self.blue_code_file)
#        self.new_file_time = datetime.utcfromtimestamp(unixtime)
#        return 69
#        if not hasattr(self, blue_change_time)
#           or self.new_file_time != self.blue_change_time:
#            if os.exiblue_code_file ) {
#             self.bluecode} = readBluecodeFile(blue_code_file)
#             self.blue_change_time} = (stat(blue_code_file))[9]
#         }
#         else {
#             self.prime()
#         }
#     }
#        return self.bluecode

    def getBluecode(self):

        return self.bluecode

    def setBluecode(self, bc):

        self.bluecode = bc

    def clear(self):

        try:
            os.unlink(self.blue_code_file)
        except OSError:
            pass
        self.bluecode = self.priming_bluecode
        self.blue_change_time = 0
        return self.bluecode

    def mysymlink(self, frm, to):
        self.logger.debug("going to symlink {} to {}".format(frm, to)),
        try:
            os.symlink(frm, to)
        except OSError:
            self.logger.critical("failed symlinking {} to {}".format(frm, to))

    def save_is_blueist_stash(self, imageset):

        stash_fn = "{}.jpg".format(str(self.bluecode))
        stash_dir = sc6_general.get_image_dir(imageset.dt, "stash", self.mode)
        stash_link = os.path.join(stash_dir, stash_fn)
        current_link = os.path.join(stash_dir, "current.jpg")

        self.mysymlink(imageset.output, stash_link)

        # unlink the current link if it's there
        try:
            os.unlink(current_link)
        except OSError:
            pass

        self.mysymlink(imageset.output, current_link)

# sub save_is_blueist_local {
#     my ( self, bf_50pct, bf_orig ) = @_
#     bc = self.bluecode]
#     blueist_file_50pct = get_www_dir("", main::mode) . self.config['BlueCode']['BlueistImage'} . "_50pct"
#     blueist_file_orig = get_www_dir("", main::mode) . self.config['BlueCode']['BlueistImage'} . "_orig"
#
#     # local copies
#     copy(bf_50pct, blueist_file_50pct) or die "Can't copy bf_50pct to blueist_file_50pct: !\n"
#     copy(bf_orig, blueist_file_orig) or die "Can't copy bf_orig to blueist_file_orig: !\n"
#     print("Bluecode copy: bf_50pct to blueist_file_50pct\n" if ( main::debug )
#     print("Bluecode copy: bf_orig to blueist_file_orig\n" if ( main::debug )
#
# }
#
    def cache(self):

        with open(self.blue_code_file, 'w') as file:
            file.write(str(self.bluecode))
        self.logger.debug("writing bluecode file locally.  Current \
            bluecode: {}".format(self.bluecode))
        self.blue_change_time = datetime.now(pytz.timezone(self.tzname))

    def prime(self):

        if os.path.exists(self.blue_code_file):
            self.readBluecodeFile()
            self.logger.debug("Bluecode file ({}) found, priming with it".format(self.bluecode))
        else:
            self.bluecode = self.priming_bluecode
            self.logger.debug("No bluecode file ({}), priming with priming_bluecode".format(self.bluecode))

    def readBluecodeFile(self):
        self.logger.debug("going to read bluecode file ({})".format(self.blue_code_file))
        try:
            with open(self.blue_code_file) as f:
                bc = f.read()
        except OSError as error:
            print(error)
            sys.exit()

        try:
            self.bluecode = float(bc.rstrip())
        except ValueError:
            self.logger.info("issues with bluecode file ({}) we're going to junk it".format(self.blue_code_file))
            self.clear()


if __name__ == '__main__':

    bcs = BCS(debug=True)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    bcs.logger.addHandler(handler)

    print("bluecode:", bcs.bluecode)
#    print(bcs.checkBluecode)
#    print(bcs.getConfirmedBluecode)
    iset = sc6_image.ImageSet()
    iset.print_my_dirs()
    print("going to fetch")
    ret = iset.fetch()
    print(ret)
    if not ret:
        print("fetch failed")
    else:
        print(bcs.checkBluecode(iset))
