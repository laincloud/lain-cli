# -*- coding: utf-8 -*-
import sys
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_sdk.util import error, warn, info
from lain_cli.utils import lain_yaml
from lain_cli.validate import validate_only_warning


@arg('--release', help="build from build image if it exists")
@arg('--push',    help="tag release and meta image with version and push to registry")
def build(push=False, release=False):
    """
    Build release and meta images
    """

    info("Building meta and release images ...")
    validate_only_warning()
    yml = lain_yaml()
    meta_version = yml.repo_meta_version()
    use_prepare = docker.exist(yml.img_names['prepare'])
    use_build = release and docker.exist(yml.img_names['build'])
    release_suc, release_name = yml.build_release(use_prepare, use_build)
    (meta_suc, meta_name) = (False, '') if not release_suc else yml.build_meta()
    if not (release_suc and meta_suc):
        sys.exit(1)
    if meta_version is None:
        warn("please git commit.")
    if push:
        if meta_version is None:
            error("need git commit SHA1.")
            return None
        tag_release_name = yml.tag_meta_version(release_name)
        docker.push(tag_release_name)

        tag_meta_name = yml.tag_meta_version(meta_name)
        docker.push(tag_meta_name)
    info("Done lain build.")
