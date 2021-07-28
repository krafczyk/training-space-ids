import pytest

class TestC3Basic:
    def test_c3_exists(self, c3):
        assert c3 is not None