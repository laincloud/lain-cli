# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

from lain_sdk.util import error, info
import lain_sdk.mydocker as docker
from lain_cli.utils import check_phase, lain_yaml, get_domain


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def push(phase):
    """
    Push release and meta images
    """

    check_phase(phase)
    info("Pushing meta and release images ...")
    yml = lain_yaml(ignore_prepare=True)
    meta_version = yml.repo_meta_version()
    if meta_version is None:
        error("please git commit.")
        return None
    domain = get_domain(phase)
    registry = "registry.%s" % domain
    phase_meta_tag = docker.gen_image_name(yml.appname, 'meta', meta_version, registry)
    phase_release_tag = docker.gen_image_name(yml.appname, 'release', meta_version, registry)
    meta_code = docker.push(phase_meta_tag)
    release_code = docker.push(phase_release_tag)
    if meta_code or release_code:
        error("Error lain push.")
        sys.exit(1)
    else:
        info("Done lain push.")
