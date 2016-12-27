# -*- coding: utf-8 -*-
from argh.decorators import arg

from lain_sdk.util import info
from lain_cli.auth import SSOAccess, get_auth_header, authorize_and_check
from lain_cli.utils import check_phase, lain_yaml, reposit_app, get_domain, get_phase_stage
from lain_cli.validate import validate_only_warning


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def reposit(phase):
    """
    Initialize a repository in lain
    """

    check_phase(phase)
    validate_only_warning()
    info("Repositing ...")

    stage = get_phase_stage(phase)
    yml = lain_yaml(ignore_prepare=True, stage=stage)
    authorize_and_check(phase, yml.appname)

    access_token = SSOAccess.get_token(phase)
    auth_header = get_auth_header(access_token)

    console = "console.%s" % get_domain(phase)
    result = reposit_app(phase, yml.appname, console, auth_header)

    info("Done, %s" % result)
