# -*- coding: utf-8 -*-
from argh.decorators import arg

from lain_sdk.util import info
from lain_cli.auth import SSOAccess, get_auth_header, authorize_and_check
from lain_cli.utils import check_phase, lain_yaml, reposit_app, get_domain, LAIN_YAML_PATH
from lain_cli.validate import validate_only_warning


@arg('phase', help="lain cluster phase id, can be added by lain config save")
@arg('-c', '--config', help="the configuration file path")
def reposit(phase, config=LAIN_YAML_PATH):
    """
    Initialize a repository in lain
    """

    check_phase(phase)
    validate_only_warning(config)
    info("Repositing ...")

    yml = lain_yaml(config, ignore_prepare=True)
    authorize_and_check(phase, yml.appname)

    access_token = SSOAccess.get_token(phase)
    auth_header = get_auth_header(access_token)

    console = "console.%s" % get_domain(phase)
    result = reposit_app(phase, yml.appname, console, auth_header)

    info("Done, %s" % result)
