# -*- coding: utf-8 -*-
from wssh import client
from argh.decorators import arg

from lain_sdk.util import error
from lain_cli.auth import SSOAccess, authorize_and_check
from lain_cli.utils import check_phase, lain_yaml, get_domain


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def enter(phase, proc_name, instance_no):
    """
    enter the container of specific proc
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    authorize_and_check(phase, yml.appname)
    domain = get_domain(phase)
    access_token = SSOAccess.get_token(phase)
    header_data = ["access-token: %s" % access_token, "app-name: %s" % yml.appname, "proc-name: %s" % proc_name, "instance-no: %s" % instance_no]
    try:
    	client.invoke_shell(endpoint="wss://entry.%s/remote/?method=cli" % domain, header=header_data)
    except:
    	error("entry may not been deployed, please deploy it before using lain enter.")
