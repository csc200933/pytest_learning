import os
import pytest

@pytest.fixture(autouse=True)
def _set_env(mocker):
    mocker.patch.dict(os.environ, {"TABLE_NAME": "dummy-table"}, clear=False)