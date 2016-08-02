# -*- coding: utf-8 -*-
import humanfriendly
import requests
import json
import pprint
from argh.decorators import arg

from lain_sdk.util import error, warn, info
from lain_cli.utils import check_phase, lain_yaml, get_domain, render_proc_status, get_apptype
from lain_cli.auth import SSOAccess, authorize_and_check, get_auth_header


@arg('phase', help="lain cluster phase id, can be added by lain config save")
@arg('proc', help="proc name")
@arg('-t', '--target', help='The target app to deploy, if not set, will be the appname of the working dir')
@arg('-o', '--output', choices=['pretty', 'json', 'json-pretty'], default='pretty')
def scale(phase, proc, target=None, cpu=None, memory=None, numinstances=None, output='pretty'):
    """
    Scale proc with cpu/memory/num_instances
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    appname = target if target else yml.appname
    authorize_and_check(phase, appname)

    domain = get_domain(phase)
    console = "console.%s" % domain
    url = "http://{}/api/v1/apps/{}/procs/{}/".format(
        console, appname, proc
    )

    access_token = SSOAccess.get_token(phase)
    auth_header = get_auth_header(access_token)

    cpu, memory, numinstances = validate_parameters(cpu, memory, numinstances)

    proc_status = requests.get(url, headers=auth_header)
    if proc_status.status_code == 200:
        # proc exists
        info(
            "Start to scale Proc {} of App {} in Lain Cluster {} with domain {}".format(
                proc, appname, phase, domain
            )
        )
    elif proc_status.status_code == 404:
        # proc does not exist
        warn(
            "Proc {} of App {} does not exists in Lain Cluster {} with domain {}".format(
                proc, appname, phase, domain
            )
        )
        info("Please deploy it first")
        exit(1)
    else:
        error("shit happend: %s"%proc_status.content)
        exit(1)

    scale_results = {}

    payload1 = {}
    payload2 = {}

    if cpu is not None:
        payload1['cpu'] = cpu
    if memory is not None:
        payload1['memory'] = memory
    if len(payload1) > 0:
        info("Scaling......")
        info(str(payload1))
        scale_r = requests.patch(url, headers=auth_header,
                                     data=json.dumps(payload1), timeout=120)
        scale_results['cpu_or_memory'] = {
            'payload': payload1,
            'success': scale_r.status_code < 300
        }
        render_scale_result(scale_r, output)

    if numinstances is not None:
        payload2['num_instances'] = numinstances
    if len(payload2) > 0:
        info("Scaling...")
        info(str(payload2))
        scale_r = requests.patch(url, headers=auth_header,
                                    data=json.dumps(payload2), timeout=120)
        scale_results['num_instances'] = {
            'payload': payload2,
            'success': scale_r.status_code < 300
        }
        render_scale_result(scale_r, output)

    info("Outline of scale result: ")
    for k, v in scale_results.iteritems():
        success = v['success']
        output_func = None
        if success:
            output_func = info
        else:
            output_func = error
        output_func("  scale of {} {}".format(k, "success" if success else "failed"))
        output_func("    params: {}".format(v['payload']))


def validate_parameters(cpu, memory, numinstances):
    if all([cpu is None, memory is None, numinstances is None]):
        warn("please input at least one param in cpu/memory/numinstances")
        exit(1)

    if numinstances is not None:
        try:
            numinstances = int(numinstances)
        except ValueError:
            warn('invalid parameter: num_instances (%s) should be integer'%numinstances)
            exit(1)
        if numinstances <= 0:
            warn('invalid parameter: num_instances (%s) should > 0'%numinstances)
            exit(1)

    if cpu is not None:
        try:
            cpu = int(cpu)
        except ValueError:
            warn('invalid parameter: cpu (%s) should be integer'%cpu)
            exit(1)
        if cpu < 0:
            warn('invalid parameter: cpu (%s) should >= 0'%cpu)
            exit(1)

    if memory is not None:
        memory = str(memory)
        try:
            humanfriendly.parse_size(memory)
        except humanfriendly.InvalidSize:
            warn('invalid parameter: memory (%s) humanfriendly.parse_size(memory) failed'%memory)

    return cpu, memory, numinstances


def render_scale_result(scale_result, output):
    try:
        result = scale_result.json()
        msg = result.pop('msg', '')
        if msg:
            print msg.decode('string_escape')
        info("proc status: ")
        render_proc_status(result.get('proc'), get_apptype(), output=output)
    except Exception:
        pprint.pprint(scale_result.content)
