#!/usr/bin/python3

import os
import sys
import time
sys.path.append('/usr/local/cam/lib/pythonlib')
import bucket_shiz
import sc6_sun
import logging
import logging.config
import yaml

with open('/usr/local/cam/conf/config.yml', 'r') as file:
    config_root = yaml.safe_load(file)
config = config_root['prod']

with open(config['Logging']['LogConfig'], 'rt') as f:
    lconfig = yaml.safe_load(f.read())
logging.config.dictConfig(lconfig)

# create logger
logger = logging.getLogger('sc6_general')


def mymkdir(d):
    try:
        os.mkdir(d, 0o0775)
    except FileExistsError as error:
        pass
    except OSError as error:
        print("can't make dir {}: {}".format(d, error))


def get_ci(dt, size, mode, dir_type):
    try:
        ci = config['Directories'][dir_type][mode]
    except KeyError:
        print("missing correct mode ('test', 'prod', etc.).  got {}".format(
            mode))
        return None

    mymkdir(ci)

    return(ci)


def get_www_dir(dt, size, mode):

    return get_ci(dt, size, mode, 'www')


def get_www_public_dir(dt, size, mode):

    return get_ci(dt, size, mode, 'www_public')


def get_video_dir(dt, size, mode):

    return get_ci(dt, size, mode, 'video')


def get_video_file(dt, size, postfix, mode):
    disposable = config['Video']['Daily']['Disposable']
    if disposable:
        pid = os.getpid()
        file = "{}output_{}_{}.{}".format(get_video_dir(dt, size, mode),
                                          size,
                                          pid,
                                          postfix)
    else:
        file = "{}output_{}.{}".format(get_video_dir(dt, size, mode),
                                       size,
                                       postfix)
    return file


def dt2epoch(dt):
    return(time.mktime(dt.timetuple()))


def get_image_dir(dt, size, mode):

    ci = get_ci(dt, size, mode, 'cam_images')

    o = "%s/%4d/%02d/%02d/%s/",
    o = "{}/{}/{}/".format(ci, dt.strftime("%Y/%m/%d"), size)

    mymkdir(o)

    return o


if __name__ == '__main__':

    mysun = sc6_sun.SC6Sun()
    dt = mysun.get_dt()
    out = get_video_file(dt, 'orig', 'mp4', 'test')
    print(out)

    try:
        os.rmdir("/tmp/junkdir")
    except OSError as error:
        pass
    mymkdir("/tmp/junkdir")
    mymkdir("/tmp/junkdir")
    try:
        os.rmdir("/tmp/junkdir")
    except OSError as error:
        pass
