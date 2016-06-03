from watchdog.events import PatternMatchingEventHandler


class DownloadEventHandler(PatternMatchingEventHandler):
    """
    Matches given patterns with file paths associated with occurring events.

    patterns=None (defaults to ["*"] in pathtools)
    ignore_patterns=None (defaults to None)
    ignore_directories=False
    case_sensitive=False
    """

    def on_create(self, event):
        pass


class EmptyFileError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def validate_json_file(path):
    with open(path, 'rb', buffering=1024) as f:
        f.read()  # it'll block until EOF
