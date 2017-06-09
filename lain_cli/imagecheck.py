# -*- coding: utf-8 -*-
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_sdk.util import error, info
from lain_cli.utils import lain_yaml, check_phase, get_domain, LAIN_YAML_PATH


def _check_phase_tag(phase, config):
    yml = lain_yaml(config, ignore_prepare=True)
    meta_version = yml.repo_meta_version()
    if meta_version is None:
        error("please git commit.")
        return None
    domain = get_domain(phase)
    registry = "registry.%s" % domain
    metatag = "meta-%s"%meta_version
    releasetag = "release-%s"%meta_version
    tag_list = docker.get_tag_list_in_registry(registry, yml.appname)
    tag_ok = True
    if metatag not in tag_list:
        tag_ok = False
        error("%s/%s:%s not exist." % (registry, yml.appname, metatag))
    else:
        info("%s/%s:%s exist." % (registry, yml.appname, metatag))
    if releasetag not in tag_list:
        tag_ok = False
        error("%s/%s:%s not exist." % (registry, yml.appname, releasetag))
    else:
        info("%s/%s:%s exist." % (registry, yml.appname, releasetag))
    return tag_ok


@arg('phase', help="lain phase, can be added by lain config save")
@arg('-c', '--config', help="the configuration file path")
def check(phase, config=LAIN_YAML_PATH):
    """
    Check current version of release and meta images in the remote registry
    """

    check_phase(phase)
    tag_ok = _check_phase_tag(phase, config)
    if tag_ok:
        info("Image Tag OK in registry")
    else:
        error("Image Tag not OK in registry")
