# -*- coding: utf-8 -*-
from argh.decorators import arg
from entryclient import EntryClient
from lain_sdk.util import error
from lain_cli.auth import SSOAccess, authorize_and_check, get_auth_header
from lain_cli.utils import check_phase, lain_yaml, get_domain

import os
import requests


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
    auth_header = get_auth_header(access_token)
    console = "console.%s" % get_domain(phase)
    app_url = ("http://%s/api/v1/apps/%s/procs/%s" %
               (console, yml.appname, proc_name))
    app_r = requests.get(app_url, headers=auth_header)
    container_id = ""
    if app_r.status_code == 200:
        containers = app_r.json()["proc"]["pods"]
        inst_no_env = "DEPLOYD_POD_INSTANCE_NO=%s" % instance_no
        for container in containers:
            if inst_no_env in container["envs"]:
                container_id = container["containerid"]
                break
    elif app_r.status_code == 404:
        error('The proc %s is not found' % proc_name)
        exit(1)
    else:
        error("shit happend")
        exit(1)

    if not container_id:
        error('The container is not found %s-%s' % (proc_name, instance_no))
        exit(1)

    client = EntryClient()
    term_type = os.environ.get("TERM", "xterm")
    endpoint = "wss://entry.%s/enter" % domain
    header_data = ["access-token: %s" % access_token,
                   "app-name: %s" % "entry",
                   "container-id: %s" % container_id,
                   "term-type: %s" % term_type]
    try:
        client.invoke_shell(endpoint, header=header_data)
    except:
        error("Server stops the connection. Ask admin for help.")
