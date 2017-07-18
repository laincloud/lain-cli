# -*- coding: utf-8 -*-
import requests
import json
import pprint
from sys import stdout
from time import sleep
from argh.decorators import arg

from lain_sdk.util import error, info
from lain_cli.auth import SSOAccess, authorize_and_check, get_auth_header
from lain_cli.utils import check_phase, get_domain, lain_yaml, is_resource_instance
from lain_cli.utils import reposit_app, get_version_lists, get_app_state
from lain_cli.utils import render_app_status, render_proc_status


@arg('phase', help="lain cluster phase id, can be added by lain config save")
@arg('-v', '--version', help='The specify version of the app to deploy')
@arg('-t', '--target', help='The target app to deploy, if not set, will be the appname of the working dir')
@arg('-p', '--proc', help='The proc need to deploy, should not be used with argh -v')
@arg('-o', '--output', choices=['pretty', 'json', 'json-pretty'], default='pretty')
def deploy(phase, version=None, target=None, proc=None, output='pretty'):
    """
    Deploy specific proc in the app or the whole app
    """

    check_phase(phase)
    yml = lain_yaml(ignore_prepare=True)
    appname = target if target else yml.appname
    authorize_and_check(phase, appname)

    console = "console.%s" % get_domain(phase)
    access_token = SSOAccess.get_token(phase)
    auth_header = get_auth_header(access_token)

    if proc:
        deploy_proc(proc, appname, console, auth_header, output)
    else:
        if not is_resource_instance(appname):
            reposit_app(phase, appname, console, auth_header)
        deploy_app(phase, appname, console, auth_header, version, output)


def deploy_app(phase, appname, console, auth_header, version, output):
    info("Begin deploy app %s to %s ..." % (appname, phase))

    app_url = "http://%s/api/v1/apps/%s/" % (console, appname)
    apps_url = "http://%s/api/v1/apps/" % console

    app_r = requests.get(app_url, headers=auth_header)
    former_version, deploy_version = None, version
    if app_r.status_code == 200:
        operation = "upgrading"
        deploy_params = None
        if not is_resource_instance(appname):
            former_version = app_r.json()["app"]["metaversion"]
            exist, valid_version = check_meta_version(phase, appname, deploy_version)
            if not exist:
                print_available_version(deploy_version, valid_version)
                exit(1)

            if deploy_version:
                deploy_params = {"meta_version": deploy_version}
            else:
                deploy_version = valid_version
        
        deploy_r = requests.put(app_url, headers=auth_header, json=deploy_params)
    elif app_r.status_code == 404:
        operation = "deploying"
        payload = {'appname': appname}
        deploy_r = requests.post(apps_url, headers=auth_header,
                                 data=json.dumps(payload), timeout=120)
    else:
        error("shit happend: %s" % app_r.content)
        exit(1)

    if deploy_r.status_code < 300:
        if output != 'pretty':
            info("%s" % deploy_r.json()['msg'])
            info("app status: ")
            render_app_status(deploy_r.json()['app'], output=output)
        else:
            result = check_deploy_result(operation, console, appname, auth_header)
            if result != 'Done':
                error("deploy latest version of %s to %s failed: %s" % (appname, phase, result))
                exit(1)
        if former_version:
            info("app {} deploy operation:".format(appname))
            info("    last version: {}".format(former_version))
            info("    this version: {}".format(deploy_version))
            info("if shit happened, rollback your app by:")
            info("    lain deploy -v {}".format(former_version))
    else:
        error("deploy latest version of %s to %s failed: %s" % (appname, phase, deploy_r.json()['msg']))
        exit(1)

def check_deploy_result(operation, console, appname, auth_header):
    i = 0
    while True:
        s = (i % 3 + 1) * '.'
        if len(s) < 3:
            s = s + (3 - len(s)) * ' '
        i += 1
        stdout.write("\r%s... %s " % (operation, s))
        stdout.flush()
        sleep(0.5)
        result = app_status(console, appname, auth_header)
        if result:
            stdout.write("\r%s... %s. " % (operation, result))
            stdout.flush()
            stdout.write("\n")
            return result


def app_status(console, appname, auth_header):
    app_url = "http://%s/api/v1/apps/%s/" % (console, appname)
    app_r = requests.get(app_url, headers=auth_header)
    if app_r.status_code == 200:
        app_status = app_r.json()["app"]
        if get_app_state(app_status) != 'unhealthy':
            return "Done"
        elif app_status['deployerror']:
            return app_status['deployerror']
        else:
            return None


def deploy_proc(proc, appname, console, auth_header, output):
    info("Begin deploy proc %s from app %s ..." % (proc, appname))

    url = "http://%s/api/v1/apps/%s/procs/" % (console, appname)
    payload = {'procname': proc}
    deploy_r = requests.post(url, headers=auth_header,
                                 data=json.dumps(payload), timeout=120)
    if deploy_r.status_code < 300:
        info("deploy proc %s successfully." % proc)
        info("deploy result detail:")
        try:
            result = deploy_r.json()
            msg = result.pop('msg', '')
            if msg:
                print msg.decode('string_escape')
            info("proc status: ")
            render_proc_status(result.get('proc'), output=output)
        except Exception:
            pprint.pprint(deploy_r.content)
    else:
        error("deploy proc %s fail : %s" % (proc, deploy_r.json()['msg']))
        exit(1)

def print_available_version(version, version_list):
    if not version_list:
        error("No available versions, please push first.")
        return
    if version:
        error("Version %s not exist." % version)
    info("Below are the available versions: ")
    for version in version_list:
        print(version)


def check_meta_version(phase, appname, deploy_version=None):
    version_list = get_version_lists(phase, appname)
    if not version_list:
        return False, None
    if not deploy_version:
        return True, version_list[0]
    if deploy_version not in version_list:
        return False, version_list
    return True, deploy_version
