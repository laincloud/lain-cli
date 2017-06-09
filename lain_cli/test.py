# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

from lain_cli.utils import lain_yaml, LAIN_YAML_PATH


@arg('-c', '--config', help="the configuration file path")
def test(config=LAIN_YAML_PATH):
    """
    Build test image and run test scripts defined in lain.yaml
    """

    if not lain_yaml(config).build_test()[0]:
        sys.exit(1)
    else:
        sys.exit(0)
