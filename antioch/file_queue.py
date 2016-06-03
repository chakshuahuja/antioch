import queue
import glob
import os


def start_queue(callback, folder_path):
    q = queue.Queue()

    add_json_files_to_queue(q, folder_path)
    print('Queue size: ', q.qsize())

    worker(q, callback)


def add_json_files_to_queue(q, folder_path):
    glob_path = os.path.join(folder_path, "*.json")
    print('glob path: ', glob_path)
    for json_file in glob.glob(glob_path):
        q.put(json_file)


def worker(q, callback):
    while True:
        print('Queue size: ', q.qsize())
        item = q.get(block=True, timeout=1)

        if item is None:
            break

        callback(item)

        if q.empty():
            break
