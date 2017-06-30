# -*- coding: utf-8 -*-

from lain_cli.validate import _validate

class TestLainValidate:

    def test_lain_validate(self):
        valid, _ = _validate()
        assert valid == True