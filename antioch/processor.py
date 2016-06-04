
import re
import os
import time
import glob
import json
import logging
import subprocess
import datetime

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from antioch.core import config

logger = logging.getLogger('antioch.processor')


def time_from_str(t):
    h, m, s = map(int, t.split(':'))
    return s + (m * 60) + (h * 60 * 60)


class JsonFileHandler(RegexMatchingEventHandler):
    def on_created(self, event):
        logger.info('event handled ' + str(event))
        process_file(event.src_path)


def move_to_error(f, msg=None):
    if msg:
        logger.error(msg)
    _, name = os.path.split(f)
    destination = os.path.join(config.ERROR_FOLDER_LOCATION, name)
    os.rename(f, destination)
    logger.info('moved file to ' + destination)


def process_file(f):
    logger.info('processing file ' + f)
    try:
        data = json.load(open(f, 'r'))
    except IOError as e:
        move_to_error(f, msg='error loading json ' + f)
        return

    # track this attempt to process the movie file
    data.setdefault('processing_attempted', list()).append(str(datetime.datetime.utcnow()))

    json_fullpath = f

    basename = os.path.basename(f)
    folder, _ = os.path.split(f)
    sha_name, _ = os.path.splitext(basename)

    movie_fullpath = os.path.join(folder, sha_name + '.movie')

    if not os.path.exists(movie_fullpath):
        move_to_error(f, msg='no associated movie file with json ' + basename)
        return

    d = data['media_info'] = dict()

    # get media information from this movie file
    result = subprocess.Popen(
        ["ffprobe", movie_fullpath],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # process the file for additional metadata found with ffmpeg
    for line in result.stdout.readlines():
        line = str(line)
        if 'Duration' in line:
            # get the duration of the video in seconds
            duration = re.search(r'\d\d:\d\d:\d\d', line, re.I)
            if not duration:
                continue
            t_str = duration.group()
            d['duration'] = t_str
            d['duration_seconds'] = time_from_str(t_str)

            bitrate = re.search(r'(\d+) kb/s', line, re.I)
            if not bitrate:
                continue
            d['bitrate'] = bitrate.group()

        if 'Stream #' in line and 'Video' in line:
            resolution = re.search(r' \d+x\d+ ', line, re.I)
            if not resolution:
                continue
            r_str = resolution.group()
            width, height = r_str.strip().split('x')
            d['resolution'] = {
                'width': int(width),
                'height': int(height)
            }

    with open(json_fullpath, 'w') as out_file:
        out_file.write(json.dumps(data, indent=4))

    # move the files to the pickup folder
    new_file = os.path.join(config.PICKUP_FOLDER_LOCATION, sha_name)
    os.rename(json_fullpath, new_file + '.json')
    os.rename(movie_fullpath, new_file + '.movie')

    logger.info('finished processing ' + sha_name)


def process_existing(path):
    if not os.path.exists(path) or not os.path.isdir(path):
        logger.error('not a valid path: ' + path)
        return
    for f in glob.iglob(os.path.join(path, '*.json')):
        process_file(f)


if __name__ == '__main__':
    # this is where things are going to be showing up!
    path = config.DROP_FOLDER_LOCATION

    # if anything is in there while the daemon wasn't running
    # we need to process it first
    process_existing(path)

    observer = Observer()
    observer.schedule(
        JsonFileHandler([r'.*\.json'], case_sensitive=False),
        path,
        recursive=False  # we dont' want to go into ``errors`` folder.
    )
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
