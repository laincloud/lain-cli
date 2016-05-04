# -*- coding: utf-8 -*-
import sys

from lain_sdk.util import info, error
from lain_cli.utils import lain_yaml
from lain_cli.validate import validate_only_warning


def prepare():
    """
    Build prepare image
    """

    validate_only_warning()
    info("Generating prepare image...")
    if not lain_yaml().build_prepare()[0]:
        error("Error lain prepare.")
        sys.exit(1)
    else:
        info("Done lain prepare.")
        sys.exit(0)

