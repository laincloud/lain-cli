# -*- coding: utf-8 -*-
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_sdk.util import error, info
from lain_cli.utils import check_phase, lain_yaml, get_domain


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def tag(phase):
    """
    Tag release and meta images
    """

    check_phase(phase)
    info("Taging meta and relese image ...")
    yml = lain_yaml(ignore_prepare=True)
    meta_version = yml.repo_meta_version()
    if meta_version is None:
        error("please git commit.")
        return None
    domain = get_domain(phase)
    registry = "registry.%s" % domain
    meta_tag = "%s:meta-%s" % (yml.appname, meta_version)
    release_tag = "%s:release-%s" % (yml.appname, meta_version)
    phase_meta_tag = docker.gen_image_name(yml.appname, 'meta', meta_version, registry)
    phase_release_tag = docker.gen_image_name(yml.appname, 'release', meta_version, registry)
    meta_code = docker.tag(meta_tag, phase_meta_tag)
    release_code = docker.tag(release_tag, phase_release_tag)
    if meta_code or release_code:
        error("Error lain tag.")
    else:
        info("Done lain tag.")
