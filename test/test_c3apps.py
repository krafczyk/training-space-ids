import pytest

class TestC3Basic:
    def test_c3_exists(self, c3):
        assert c3 is not None

    def test_c3_systemInformation(self, c3):
        info = c3.SystemInformation.about()
        assert hasattr(info, 'serverVersion')
        print(info.serverVersion)