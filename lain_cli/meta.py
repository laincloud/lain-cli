# -*- coding: utf-8 -*-
from argh.decorators import arg

from lain_sdk.util import error, info
from lain_cli.utils import lain_yaml, LAIN_YAML_PATH


@arg('-c', '--config', help="the configuration file path")
def meta(config=LAIN_YAML_PATH):
    """
    Show current meta version
    """

    meta_version = lain_yaml(config, ignore_prepare=True).repo_meta_version()
    if meta_version is None:
        error("please git commit.")
    else:
        info("meta version : %s" % lain_yaml(ignore_prepare=True).repo_meta_version())
