# -*- coding: utf-8 -*-
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_sdk.util import warn, info
from lain_cli.auth import SSOAccess
from lain_cli.utils import check_phase, get_domain


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def logout(phase):
    """
    Logout specific phase
    """

    check_phase(phase)
    domain = get_domain(phase)
    logout_success = SSOAccess.clear_token(phase)
    if logout_success:
    	docker.logout('registry.%s'%domain)
        info("Logout successfully!")
    else:
        warn('Logout failed!')
