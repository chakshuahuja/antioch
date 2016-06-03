import pytest


class TestValidateJsonFile():

    def test_file_does_not_exist(self):
        from antioch.event_handler import (
            validate_json_file,
        )

        with pytest.raises(FileNotFoundError):
            validate_json_file('/tmp/doesntexist.noop')
