# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

from lain_sdk.util import info, error
from lain_cli.utils import lain_yaml, LAIN_YAML_PATH
from lain_cli.validate import validate_only_warning


@arg('-c', '--config', help="the configuration file path")
def prepare(config=LAIN_YAML_PATH):
    """
    Build prepare image
    """

    validate_only_warning(config)
    info("Generating prepare image...")
    if not lain_yaml(config).build_prepare()[0]:
        error("Error lain prepare.")
        sys.exit(1)
    else:
        info("Done lain prepare.")
        sys.exit(0)

