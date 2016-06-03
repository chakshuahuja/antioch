import os
import pytest
import shutil
import unittest.mock as mock

from collections import namedtuple


TempDir = namedtuple('TempDir', 'path files')


@pytest.yield_fixture
def generate_json_files():

    folder = '/tmp/json_file'
    os.mkdir(folder)

    def wrapper(amount=3):
        temp_files = []
        for number in range(0, amount):
            file_name = '{}-temp_file.json'.format(number)
            full_path = os.path.join(folder, file_name)
            temp_files.append(full_path)
            with open(full_path, 'wb+'):
                pass

        return TempDir(folder, temp_files)

    yield wrapper
    shutil.rmtree(folder)


class TestFileQueue():

    def test_start_queue(self, generate_json_files):
        from antioch.file_queue import start_queue

        m = mock.Mock(return_value=None)

        temp_dir = generate_json_files()
        print(temp_dir)

        calls = [mock.call(file_name)
                 for file_name in reversed(temp_dir.files)]

        start_queue(m, temp_dir.path)
        m.assert_has_calls(calls)
