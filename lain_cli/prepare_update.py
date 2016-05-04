# -*- coding: utf-8 -*-
import sys

from lain_cli.utils import lain_yaml
from lain_cli.validate import validate_only_warning


def prepare_update():
    """
    Update prepare image based on existed prepare image
    """

    validate_only_warning()
    if not lain_yaml().update_prepare()[0]:
        sys.exit(1)
    else:
        sys.exit(0)
