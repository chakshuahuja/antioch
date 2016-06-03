import os
import json
import uuid
import logging
import datetime
import glob
import requests

from requests import exceptions as RequestErrors
from concurrent.futures import ThreadPoolExecutor, as_completed

from antioch.core import config


logger = logging.getLogger(__name__)

console = logging.StreamHandler()
console.setFormatter(logging.Formatter(
    fmt='%(asctime)s %(levelname)-5s %(name)-40s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
))
logger.addHandler(console)
logger.setLevel(logging.DEBUG)
logger.propagate = False


def find_files_by_extension(path, extension='json'):
    logger.info('find all json files at path: ' + path)
    return glob.glob(os.path.join(path, '**/**/*.{}'.format(extension)))

def videos_by_container(path):
    all_files = find_files_by_extension(path)
    error_files = dict()
    process_files = dict()

    logger.info('found %d files' % len(all_files))

    for fname in all_files:
        if os.path.basename(fname) == 'category.json':
            continue

        with open(fname, 'r') as ins_file:
            try:
                d = json.loads(ins_file.read())
            except Exception as e:
                error_files[fname] = str(e)
                continue

        videos = d.get('videos', list())
        types = list()

        for video in videos:
            vid_type = video.get('type', None)
            if vid_type is None:
                continue
            types.append(vid_type)
            vid_type_category = process_files.setdefault(vid_type, dict())
            vid_type_category[fname] = video

    if error_files:
        for f in error_files:
            logger.error('Error with file: ' + f)
    return process_files


def download_youtube(url, timeout, chunk_size=DEFAULT_CHUNKSIZE):
    try:
        yt = YouTube(url)

        video_formats = yt.get_videos()

        yt.set_filename(gen_filename(DROP_FOLDER_LOCATION))

        print

    except Exception as e:
        logger.error(e)
        return None

    else:
        pass


def download_other(obj, timeout, chunk_size=config.DEFAULT_CHUNKSIZE):
    url = obj.get('url', None)
    if url is None:
        return None

    logger.info('downloading video: ' + url)

    try:
        response = requests.get(url, stream=True, timeout=timeout)

    except RequestErrors.RequestException as e:
        logger.error(e)
        return None

    else:
        filename = os.path.join(config.DROP_FOLDER_LOCATION, uuid.uuid4().hex + '.movie')
        with open(filename, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                out_file.write(chunk)
        return filename


def download_videos(vid_type: str, video_list: dict):
    actions = {
        'youtube': download_youtube
    }

    logger.info('saving files to: ' + config.DROP_FOLDER_LOCATION)

    download_fn = actions.get(vid_type, download_other)
    return_status = dict()

    with ThreadPoolExecutor(max_workers=config.DEFAULT_THREAD_COUNT) as x:
        future_to_obj = {x.submit(download_fn, v, timeout=config.REQ_TIMEOUT): k for k, v in video_list.items()}

        for future in as_completed(future_to_obj):
            original_json = future_to_obj.get(future)
            logger.info('finished processing: ' + original_json)

            try:
                movie_filename = future.result()

                if movie_filename is None:
                    raise IOError(original_json)

            except Exception as exc:
                logger.error('error downloading movie from %s: %s' % (original_json, exc))
                was_error = True
                movie_filename = None
                _, fname = os.path.split(original_json)
                new_filename = os.path.join(config.ERROR_FOLDER_LOCATION, fname)

            else:
                logger.info('successfully downloaded movie: ' + movie_filename)
                was_error = False
                _, fname = os.path.split(movie_filename)
                fname, _ = os.path.splitext(fname)
                new_filename = os.path.join(config.DROP_FOLDER_LOCATION, '%s.json' % fname)

            _key = 'success' if not was_error else 'failure'

            # add our return to the failures or successes
            return_status.setdefault(_key, list()).append(new_filename)

            with open(new_filename, 'w') as out_file, open(original_json, 'r') as ins_file:
                data = json.loads(ins_file.read())

                # modify the data being written to the JSON file
                data.setdefault('container_type', vid_type)

                # preserve the original data filename
                data.setdefault('original_file', original_json)

                # keep track of the last time we attempted to
                # download the video file...this is useful if
                # the JSON file got put in the `error` queue and it
                # needs to be attempted again.
                data.setdefault('download_attempted', list()).append(str(datetime.datetime.utcnow()))

                # remove the video keys from our new downloads
                # but only if we're planning on removing the original

                if config.REMOVE_JSON_ON_SUCCESS:
                    del data['videos']

                if not was_error:
                    movie_fstat = os.stat(movie_filename)
                    # successfully downloaded the movie file? save its filesize
                    data.setdefault('movie_file', movie_filename)
                    data.setdefault('filesize', movie_fstat.st_size)
                else:
                    # otherwise, we don't know the time
                    data.setdefault('movie_file', None)
                    data.setdefault('filesize', -1)

                out_file.write(json.dumps(data, indent=4))

            if config.REMOVE_JSON_ON_SUCCESS:
                logger.info('removing json file: ' + original_json)
                os.remove(original_json)

    return return_status


def main():
    for folder in config.DEFAULT_FOLDERS:
        if not os.path.exists(folder):
            logger.info('creating folder: ' + folder)
            os.makedirs(folder)

    videos = videos_by_container(config.READ_FROM_DIRECTORY)
    # (key, value) for items
    for vid_type, items in videos.items():
        download_videos(vid_type, items)


if __name__ == '__main__':
    main()
