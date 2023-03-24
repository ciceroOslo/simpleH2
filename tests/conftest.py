import os.path

import pytest

# from simpleh2 import simpleh2

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test-data")


@pytest.fixture(scope="session")
def test_data_dir():
    return TEST_DATA_DIR
