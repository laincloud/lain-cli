# -*- coding: utf-8 -*-
import pprint
import requests
from argh.decorators import arg

from lain_sdk.util import info, error
from lain_cli.auth import SSOAccess, get_auth_header, authorize_and_check
from lain_cli.utils import TwoLevelCommandBase, check_phase, get_domain, lain_yaml


class MaintainerCommands(TwoLevelCommandBase):
    '''
    allow maintain the maintainer of app in lain, only used when the auth is open
    '''

    @classmethod
    def subcommands(self):
        return [self.show, self.add, self.delete]

    @classmethod
    def namespace(self):
        return "maintainer"

    @classmethod
    def help_message(self):
        return "maintainer operation: including add, delete or show maintainers of the app"

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    def show(cls, phase, username=None):
        """
        show maintainers list or specical maitainer message of app in different phase

        username: sso username
        """
        
        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        console = "console.%s" % get_domain(phase)

        maintainer_url = "http://%s/api/v1/repos/%s/maintainers/" % (
            console, yml.appname)
        if username:
            maintainer_url += '%s/' % username
        
        show_response = requests.get(maintainer_url, headers=auth_header)
        if show_response.status_code < 300:
            info("maintainer detail:")
            pprint.pprint(show_response.json())
        else:
            error("shit happened : %s" % show_response.text)

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    @arg('username', help="sso username to add")
    @arg('role', help='role to assigned to the user', choices=['admin', 'normal'])
    def add(cls, phase, username, role):
        """
        add maintianer for different phase
        """
        
        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        console = "console.%s" % get_domain(phase)

        maintainer_url = "http://%s/api/v1/repos/%s/maintainers/" % (
            console, yml.appname)
        payload = {"username": username,
                   "role": role}

        add_response = requests.post(maintainer_url, headers=auth_header, json=payload)
        if add_response.status_code < 300:
            info("add successfully.")
        else:
            error("shit happened : %s" % add_response.text)

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    @arg('username', help="sso username")
    def delete(cls, phase, username):
        """
        delete maintianer for different phase
        """

        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        console = "console.%s" % get_domain(phase)
        
        maintainer_url = "http://%s/api/v1/repos/%s/maintainers/%s/" % (
            console, yml.appname, username)

        delete_response = requests.delete(maintainer_url, headers=auth_header)
        if delete_response.status_code < 300:
            info("delete successfully.")
        else:
            error("shit happened : %s" % delete_response.text)
