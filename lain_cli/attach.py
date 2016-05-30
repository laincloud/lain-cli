# -*- coding: utf-8 -*-
from argh.decorators import arg
from entryclient import EntryClient
from lain_sdk.util import error, info
from lain_cli.auth import SSOAccess, authorize_and_check
from lain_cli.utils import check_phase, lain_yaml, get_domain


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def attach(phase, proc_name, instance_no):
    """
    enter the container of specific proc
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    authorize_and_check(phase, yml.appname)
    domain = get_domain(phase)
    access_token = SSOAccess.get_token(phase)
    endpoint = "wss://entry.%s/attach" % domain
    header_data = ["access-token: %s" % access_token,
                   "app-name: %s" % yml.appname,
                   "proc-name: %s" % proc_name,
                   "instance-no: %s" % instance_no]
    try:
        client = EntryClient(endpoint, header=header_data)
        info("Start to attach the stdout/stderr of the container. Press <Ctrl+c> to stop...")
        client.attach_container()
    except KeyboardInterrupt:
        pass
    except:
        error("Server stops the connection. Ask admin for help.")
