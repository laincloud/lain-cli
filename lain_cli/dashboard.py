# -*- coding: utf-8 -*-
import requests
from argh.decorators import arg

from lain_sdk.util import info, error
from lain_cli.auth import SSOAccess, get_auth_header
from lain_cli.utils import get_domain, get_app_state, check_phase


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def dashboard(phase):
    """
    Basic dashboard of Lain
    """

    check_phase(phase)
    print_welecome()
    print_workflows()
    console = "console.%s" % (get_domain(phase))
    access_token = SSOAccess.get_token(phase)
    auth_header = get_auth_header(access_token)

    print_available_repos(console, auth_header)
    print_available_apps(console, auth_header)


def print_welecome():
    info('##############################')
    info('#      Welcome to Lain!      #')
    info('##############################')


def print_workflows():
    info('There are two recommended workflows :')
    info('  1. lain reposit => lain prepare => lain build => lain tag => lain push => lain deploy')


def render_repo(repo):
    print("{}  ".format(repo["appname"])),


def render_app(app):
    print("{:<30}  {:<20}  {:<60}  {:<10}".format(
        app["appname"], app["apptype"], app["metaversion"], get_app_state(app)))


def print_available_repos(console, auth_header):
    repos_url = "http://%s/api/v1/repos/" % console
    repos_res = requests.get(repos_url, headers=auth_header)
    info('Available repos are :')
    if repos_res.status_code == 200:
        repos = repos_res.json()["repos"]
        for repo in repos:
            render_repo(repo)
        print('')
    else:
        error("shit happened : %s" % repos_res.content)


def print_available_apps(console, auth_header):
    apps_url = "http://%s/api/v1/apps/" % console
    apps_res = requests.get(apps_url, headers=auth_header)
    info('Available apps are :')
    print("{:<30}  {:<20}  {:<60}  {:<10}".format(
        "Appname", "AppType", "MetaVersion", "State"))
    if apps_res.status_code == 200:
        apps = apps_res.json()["apps"]
        for app in apps:
            render_app(app)
    else:
        error("shit happened: %s" % apps_res.content)
