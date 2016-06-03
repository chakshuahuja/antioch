
import os
import time
import logging

from watchdog.observers import Observer
from watchdog.events import RegexMatchingEventHandler

from antioch.core import config

logger = logging.getLogger('antioch.processor')

class JsonFileHandler(RegexMatchingEventHandler):
    def on_created(self, event):
        pass

def process_file(f):
    pass

def process_existing(path):
    pass

if __name__ == '__main__':
    # this is where things are going to be showing up!
    path = config.DROP_FOLDER_LOCATION

    # if anything is in there while the daemon wasn't running
    # we need to process it first
    process_existing(path)

    observer = Observer()
    observer.add_handler_for_watch(
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
