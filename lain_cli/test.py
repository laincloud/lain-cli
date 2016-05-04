# -*- coding: utf-8 -*-
import sys
from lain_cli.utils import lain_yaml


def test():
    """
    Build test image and run test scripts defined in lain.yaml
    """

    if not lain_yaml().build_test()[0]:
        sys.exit(1)
    else:
        sys.exit(0)
