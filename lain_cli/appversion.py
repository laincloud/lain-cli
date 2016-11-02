# -*- coding: utf-8 -*-
from argh.decorators import arg

from lain_sdk.util import warn, info
from lain_cli.auth import authorize_and_check
from lain_cli.utils import get_version_lists, lain_yaml, check_phase


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def appversion(phase):
    """
    Show available app versions in remote registry of lain
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    authorize_and_check(phase, yml.appname)

    version_list = get_version_lists(phase, yml.appname)
    print_available_version(version_list)


def print_available_version(version_list):
    if len(version_list) == 0:
        warn("No available release versions.")
    else:
        info("Below are the available versions: ")
        for version in version_list:
            print(version)
