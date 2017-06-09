# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

from lain_cli.utils import lain_yaml, LAIN_YAML_PATH
from lain_cli.validate import validate_only_warning


@arg('-c', '--config', help="the configuration file path")
def prepare_update(config=LAIN_YAML_PATH):
    """
    Update prepare image based on existed prepare image
    """

    validate_only_warning(config)
    if not lain_yaml(config).update_prepare()[0]:
        sys.exit(1)
    else:
        sys.exit(0)
