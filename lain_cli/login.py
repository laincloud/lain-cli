# -*- coding: utf-8 -*-
import getpass
from argh.decorators import arg

from lain_sdk.util import warn, info, error
from lain_cli.auth import sso_login, docker_login, sso_refresh
from lain_cli.utils import check_phase


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def refresh(phase):
    """
    Refresh sso token
    """

    check_phase(phase)
    refresh_success = sso_refresh(phase)
    if refresh_success:
        info("Refresh successfully!")
    else:
        warn('Refresh failed, Please try again!')


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def login(phase, cid=None, secret=None, redirect_uri=None):
    """
    Login specific phase, need open auth first

    cid: Client id get from the sso system, default: 3
    secret: Client secret get from the sso system, default: lain-cli_admin
    redirect_uri: Redirect uri get from the sso system, default: https://example.com/
    """

    check_phase(phase)
    username = raw_input('SSO Username:')
    password = getpass.getpass('SSO Password:')
    sso_login_success = sso_login(phase, cid, secret, redirect_uri, username, password)
    if not sso_login_success:
        error('sso Login failed, Please try again!')
        exit(1)

    docker_login_success = docker_login(phase, username, password)
    if not docker_login_success:
        error('docker Login failed, Please try again!')
        exit(1)

    info("Login successfully!")
