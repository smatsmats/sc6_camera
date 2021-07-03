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
import subprocess

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


def get_ci(size, dir_type):
    try:
        ci = config['Paths'][dir_type]
    except KeyError:
        print("bad or missing dir_type.  got {}".format(
            mode))
        return None

    mymkdir(ci)

    return(ci)


def get_www_dir(size, mode):

    return get_ci(size, 'www')


def get_www_public_dir(size, mode):

    return get_ci(size, 'www_public')


def get_video_dir(dt, size, mode):

    return get_ci(size, 'video')


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

    ci = get_ci(size, 'cam_images')

    o = "%s/%4d/%02d/%02d/%s/",
    o = "{}/{}/{}/".format(ci, dt.strftime("%Y/%m/%d"), size)

    mymkdir(o)

    return o

def run_cmd(cmd, debug):
    if debug:
        print("About to run command: {}".format(" ".join(cmd)))

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    ret = proc.returncode
    if debug:
        if stderr:
            stderr_d = stderr.decode('UTF-8')
            print("stderr: {}".format(stderr_d.rstrip()))
            logger.debug("stderr: {}".format(stderr_d))
        if stdout:
            stdout_d = stdout.decode('UTF-8')
            print("stdout: {}".format(stdout_d.rstrip()))
            logger.debug("stdout: {}".format(stdout_d))
        print("return code: {}\n".format(ret))
        logger.debug("return code: {}".format(ret))
    if ret != 0:
        print("Command failed: {} \
            Return: {}".format(" ".join(cmd), ret))
        sys.exit(ret)
    return(ret)


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
