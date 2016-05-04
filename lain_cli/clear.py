# -*- coding: utf-8 -*-
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_cli.utils import lain_yaml


@arg('--without', help="a string of items separated by ',', \
                        denoting images phases not to be cleared. \
                        like 'build,prepare' or 'prepare'")
def clear(without=""):
    """
    Clear images of all phases, can specify --without as filter
    """

    yml = lain_yaml(ignore_prepare=True)
    without_phases = without.split(',')
    for name in yml.img_names.values():
        if docker.get_phase(name) not in without_phases:
            docker.remove_image(name)
