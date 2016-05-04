# -*- coding: utf-8 -*-
import pprint
import requests
from argh.decorators import arg

from lain_sdk.util import info, error
from lain_cli.auth import SSOAccess, get_auth_header, authorize_and_check
from lain_cli.utils import TwoLevelCommandBase, check_phase
from lain_cli.utils import lain_yaml, get_domain


class SecretCommands(TwoLevelCommandBase):
    '''
    allow add secret files for app, lain will add the secret file into 
    image of the proc when deploying.
    '''

    @classmethod
    def subcommands(self):
        return [self.show, self.add, self.delete]

    @classmethod
    def namespace(self):
        return "secret"

    @classmethod
    def help_message(self):
        return "secret operation: including add, delete or show secret files of the app"

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    @arg('procname', help="proc fullname, eg: app.protype.proname ")
    def show(cls, phase, procname, path=None):
        """
        show secret file of special procname in different phase

        path: absolute path of config file, eg : /lain/app/config
        """

        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        
        lvault_url = "http://lvault.%s/v2/secrets?app=%s&proc=%s" % (
            get_domain(phase), yml.appname, procname)
        if path:
            lvault_url += "&path=%s" % path
        
        show_response = requests.get(lvault_url, headers=auth_header)
        if show_response.status_code < 300:
            info("secret file detail:")
            pprint.pprint(show_response.json())
        else:
            error("shit happened : %s" % show_response.text)

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    @arg('procname', help="proc fullname, eg: app.protype.proname ")
    @arg('path', help='absolute path of config file, eg : /lain/app/config')
    @arg('content', help="content of the secret file")
    def add(cls, phase, procname, path, content):
        """
        add secret file for different phase
        """

        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        proc = yml.procs.get(procname, None)
        if proc is None:
            error('proc {} does not exist'.format(procname))
            exit(1)

        lvault_url = "http://lvault.%s/v2/secrets?app=%s&proc=%s&path=%s" % (
            get_domain(phase), yml.appname, procname, path)
        payload = {"content": content}

        add_response = requests.put(lvault_url, headers=auth_header, json=payload)
        if add_response.status_code < 300:
            info("add successfully.")
        else:
            error("shit happened : %s" % add_response.text)

    @classmethod
    @arg('phase', help="lain cluster phase id, can be added by lain config save")
    @arg('procname', help="proc fullname, eg: app.protype.proname ")
    @arg('path', help='absolute path of config file, eg : /lain/app/config')
    def delete(cls, phase, procname, path):
        """
        delete secret file for different phase
        """

        check_phase(phase)
        yml = lain_yaml(ignore_prepare=True)
        authorize_and_check(phase, yml.appname)
        auth_header = get_auth_header(SSOAccess.get_token(phase))
        
        lvault_url = "http://lvault.%s/v2/secrets?app=%s&proc=%s&path=%s" % (
            get_domain(phase), yml.appname, procname, path)

        delete_response = requests.delete(lvault_url, headers=auth_header)
        if delete_response.status_code < 300:
            info("delete successfully.")
        else:
            error("shit happened : %s" % delete_response.text)
