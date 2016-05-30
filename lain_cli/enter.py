# -*- coding: utf-8 -*-
from argh.decorators import arg
from entryclient import EntryClient
from lain_sdk.util import error
from lain_cli.auth import SSOAccess, authorize_and_check
from lain_cli.utils import check_phase, lain_yaml, get_domain

import os


@arg('phase', help="lain cluster phase id, can be added by lain config save")
@arg('-t', '--target', help='The target appname to enter. If it\'s not set, it will be the appname of the working dir')
def enter(phase, proc_name, instance_no, target=None):
    """
    Enter the container of specific proc
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    appname = target if target else yml.appname
    authorize_and_check(phase, appname)
    domain = get_domain(phase)
    access_token = SSOAccess.get_token(phase)

    term_type = os.environ.get("TERM", "xterm")
    endpoint = "wss://entry.%s/enter" % domain
    header_data = ["access-token: %s" % access_token,
                   "app-name: %s" % appname,
                   "proc-name: %s" % proc_name,
                   "instance-no: %s" % instance_no,
                   "term-type: %s" % term_type]
    try:
        client = EntryClient(endpoint, header=header_data)
        client.invoke_shell()
    except:
        error("Server stops the connection. Ask admin for help.")
