#!/usr/bin/env python3

import os
import json
import uuid
import shutil
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable

import requests
from requests import exceptions as RequestErrors

logger = logging.getLogger(__name__)

DEFAULT_CHUNKSIZE = 16 * 1024
DEFAULT_THREAD_COUNT = 16
READ_FROM_DIRECTORY = r'/home/blake/code/pyvideo/pyvideo-data/data'
DROP_FOLDER_LOCATION = r'/tmp/videos'
DEFAULT_ERROR_FOLDER = os.path.join(DROP_FOLDER_LOCATION, 'errors')
DEFAULT_FOLDERS = [
    DROP_FOLDER_LOCATION,
    DEFAULT_ERROR_FOLDER
]

def find_json_files(path):
    logger.info('find all json files at path: ' + path)
    def _verify_json(f):
        return f.lower().endswith('json')
    return files_in_path(path, _verify_json)


def files_in_path(path, filter_fn=None):
    logger.info('find all files at path: ' + path)
    if filter_fn is None:
        filter_fn = lambda x: True
    found_files = list()
    for dir_name, sub_dirs, files in os.walk(path):
        for f in files:
            f = os.path.join(dir_name, f)
            if filter_fn(f):
                found_files.append(f)
    return found_files


def videos_by_container(path):
    all_files = find_json_files(path)
    error_files = dict()
    process_files = dict()

    logger.info('found %d files' % len(all_files))

    for fname in all_files:
        if fname.endswith('category.json'):
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
    pass


def download_other(obj, timeout, chunk_size=DEFAULT_CHUNKSIZE):
    url = obj.get('url', None)
    if url is None: return None
    try:
        response = requests.get(url, stream=True, timeout=timeout)
    except RequestErrors.RequestException as e:
        logger.error(e)
        return None
    else:
        filename = os.path.join(DROP_FOLDER_LOCATION, uuid.uuid4().hex + '.movie')
        with open(filename, 'wb') as out_file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                out_file.write(chunk)
        return filename

actions = {
    'youtube': download_youtube
}

def download_videos(vid_type: str, video_list: dict) -> dict:
    download_fn = actions.get(vid_type, download_other)
    return_status = dict()

    with ThreadPoolExecutor(max_workers=DEFAULT_THREAD_COUNT) as x:
        future_to_obj = {x.submit(download_fn, v, timeout=5*60):k for k, v in video_list.items()}

        for future in as_completed(future_to_obj):
            original_json = future_to_obj.get(future)

            was_error = False

            try:
                movie_filename = future.result()
            except Exception as exc:
                print('err', exc)
                was_error = True
            else:
                was_error = False

            _, fname = os.path.split(movie_filename)

            fname, _ = os.path.splitext(fname)
            fname = '%s.json' % fname

            if was_error:
                new_filename = os.path.join(DEFAULT_ERROR_FOLDER, fname)
            else:
                new_filename = os.path.join(DROP_FOLDER_LOCATION, fname)

            _key = 'success' if not was_error else 'failure'
            return_status.setdefault(_key, list()).append(new_filename)

            with open(new_filename, 'wb') as out_file:
                with open(original_json, 'rb') as ins_file:
                    out_file.write(ins_file.read())

    return return_status


def main():
    for folder in DEFAULT_FOLDERS:
        if not os.path.exists(folder):
            logger.info('creating folder: ' + folder)
            os.makedirs(folder)

    videos = videos_by_container(READ_FROM_DIRECTORY)
    # (key, value) for items
    for vid_type, items in videos.items():
        download_videos(vid_type, items)


if __name__ == '__main__':
    main()
