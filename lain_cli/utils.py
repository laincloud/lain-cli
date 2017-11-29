# coding: utf-8

import re
import os
import sys
import json
import yaml
import requests
import collections
from lain_sdk.yaml.conf import user_config
import lain_sdk.mydocker as docker
from lain_sdk.util import error, warn, info
from lain_sdk.lain_yaml import LainYaml
from subprocess import check_output
from abc import ABCMeta, abstractmethod
from tabulate import tabulate


LAIN_YAML_PATH = './lain.yaml'

VALID_TAG_PATERN = re.compile(r"^(meta)-(?P<meta_version>\S+-\S+)$")

DOMAIN_KEY = user_config.domain_key
PHASE_CHOICES = user_config.get_available_phases()

requests.packages.urllib3.disable_warnings()


class TwoLevelCommandBase(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def subcommands(self):
        '''return subcommand function list'''

    @abstractmethod
    def namespace(self):
        '''return namespace string'''

    @abstractmethod
    def help_message(self):
        '''return help message string'''


def lain_yaml_data():
    if not os.path.exists(LAIN_YAML_PATH):
        error('Missing lain.yaml under current directory')
        sys.exit(1)
    with open(LAIN_YAML_PATH) as f:
        data = f.read()
    return yaml.load(data)


def lain_yaml(ignore_prepare=False):
    if not os.path.exists(LAIN_YAML_PATH):
        error('Missing lain.yaml under current directory')
        sys.exit(1)
    return LainYaml(LAIN_YAML_PATH, ignore_prepare=ignore_prepare)


def check_phase(phase):
    if phase not in PHASE_CHOICES:
        error('phase %s not in available phases: %s.' % (phase, PHASE_CHOICES))
        warn(
            'phase can be added using: lain config save %s domain {{ domain }}' % phase)
        exit(1)


def get_domain(phase):
    domain = user_config.get_config().get(phase, {}).get(DOMAIN_KEY, None)
    if not domain:
        error('please set %s domain by "lain config save %s %s ${%s_domain}"'
              % (phase, phase, DOMAIN_KEY, phase))
        exit(1)
    return domain


def get_apptype():
    with open(LAIN_YAML_PATH, 'r') as f:
        y = yaml.safe_load(f.read())
    return y.get('apptype', 'app')


def get_meta_version_from_tag(tag):
    if tag is None:
        return None
    x = VALID_TAG_PATERN.match(tag)
    if x:
        return x.group('meta_version')
    else:
        return None


def save_config(phase, prop, value):
    p_value = {prop: value}
    _kw = {phase: p_value}
    user_config.set_config(**_kw)


def save_global_config(prop, value):
    _kw = {prop: value}
    user_config.set_global_config(**_kw)


def get_meta_versions_from_tags(tags):
    versions = []
    for tag in tags:
        version = get_meta_version_from_tag(tag)
        if version and version not in versions:
            versions.append(version)
    return versions


def get_version_lists(phase, appname):
    tag_list = docker.get_tag_list_in_registry(
        "registry." + get_domain(phase), appname)
    version_list = available_meta_versions(tag_list)
    return version_list


def available_meta_versions(tag_list):
    versions = {}
    for k in tag_list:
        meta_version = get_meta_version_from_tag(k)
        if meta_version:
            _timestamp = float(meta_version.split('-')[0])
            versions[_timestamp] = meta_version
    ordered_versions = collections.OrderedDict(
        sorted(versions.items(), reverse=True))
    return ordered_versions.values()


def reposit_app(phase, appname, console, auth_header):
    payload = {'appname': appname}

    repo_url = "http://%s/api/v1/repos/%s/" % (console, appname)
    repos_url = "http://%s/api/v1/repos/" % console
    repo_r = requests.get(repo_url, headers=auth_header)
    if repo_r.status_code == 404:
        repos_r = requests.post(repos_url, headers=auth_header,
                                data=json.dumps(payload), timeout=120)
        if repos_r.status_code == 201:
            return 'reposit successfully'
        else:
            error("shit happened: %s" % repos_r.content)
            exit(1)
    elif repo_r.status_code == 200:
        return "already been reposited"
    else:
        error("shit happened: %s" % repo_r.content)
        exit(1)


def get_proc_state(proc, apptype="app"):
    if apptype == "resource":
        return "healthy"
    if len(proc.get("pods")) == 0:
        return "unhealthy"
    for pod in proc.get("pods"):
        if pod.get("status") != "True":
            return "unhealthy"
    return "healthy"


def get_app_state(app):
    if not app or app.get("deployerror") or len(app.get("procs")) == 0:
        return "unhealthy"
    for proc in app.get("procs"):
        if get_proc_state(proc, app.get("apptype")) == "unhealthy":
            return "unhealthy"
    if app.get("useservices"):
        for service in app.get("useservices"):
            if get_app_state(service.get("service")) != "healthy":
                return "missing service"
    if app.get("useresources"):
        for resource in app.get("useresources"):
            if get_app_state(resource.get("resourceinstance")) != "healthy":
                return "missing resource"
    return "healthy"


def render_app_status(app_status, output='pretty'):
    if not app_status:
        print("\tNot found, may not exist or has been undeployed.")
        return

    table = [
        ['appname', app_status.get('appname')],
        ['state', get_app_state(app_status)],
        ['apptype', app_status.get('apptype')],
        ['metaversion', app_status.get('metaversion')],
        ['updatetime', app_status.get('updatetime')],
        ['deploy_error', app_status.get('deployerror')]
    ]
    if output == 'pretty':
        info('App info:')
        print(tabulate(table, tablefmt='fancy_grid'))
    if output == 'json':
        print(json.dumps(app_status))
        return
    if output == 'json-pretty':
        print(json.dumps(app_status, indent=2))
        return

    if app_status.get('procs'):
        info('Proc list:')
        for proc_status in app_status.get("procs"):
            render_proc_status(proc_status, app_status.get(
                'apptype'), output=output)

    if app_status.get('portals'):
        info('Portal list:')
        for portal_status in app_status.get("portals"):
            render_portal_status(portal_status, output=output)

    if app_status.get('useservices'):
        info('Service Portal list:')
        for use_service in app_status.get("useservices"):
            render_service_portal_status(use_service, output=output)

    if app_status.get('useresources'):
        info('Use Resources list:')
        for use_resource in app_status.get("useresources"):
            render_app_status(use_resource.get(
                "resourceinstance"), output=output)

    if app_status.get('resourceinstances'):
        info('Resource Instances list:')
        for instance in app_status.get("resourceinstances"):
            render_app_status(instance, output=output)


def render_proc_status(proc_status, apptype, output='pretty'):

    table = [
        ['procname', proc_status.get('procname')],
        ['proctype', proc_status.get('proctype')],
        ['state', get_proc_state(proc_status, apptype)],
        ['memory', proc_status.get('memory')],
        ['cpu', proc_status.get('cpu')],
        ['image', proc_status.get('image')],
        ['instances', proc_status.get('numinstances')]
    ]

    if output == 'pretty':
        print(tabulate(table, tablefmt='psql'))
    elif output == 'json':
        print(json.dumps(proc_status))
        return
    elif output == 'json-pretty':
        print(json.dumps(proc_status, indent=2))
        return

    no_of_procs = len(proc_status.get('pods'))
    for idx, pod_status in enumerate(proc_status.get("pods"), start=1):
        if idx != no_of_procs:
            render_pod_status(pod_status)
        else:
            render_pod_status(pod_status, last_one=True)


def render_pod_status(pod_status, last_one=False):

    arrow_1 = '├─>'
    arrow_2 = '└─>'

    template = '{arrow} {name} ({ip}) @ Node {node_ip}'

    arrow = arrow_2 if last_one else arrow_1

    print(template.format(
        arrow=arrow,
        name=pod_status.get('containername'),
        ip=pod_status.get('containerip'),
        node_ip=pod_status.get('nodeip')
    ))


def render_portal_status(portal_status, output='pretty'):

    table = [
        ['procname', portal_status.get('procname')],
        ['memory', portal_status.get('memory')],
        ['cpu', portal_status.get('cpu')],
        ['image', portal_status.get('image')],
        ['portal_numbers', len(portal_status.get('pods'))]
    ]

    _render_protal(table, portal_status, output)


def render_service_portal_status(service_status, output='pretty'):
    portals = service_status.get('service').get('portals')
    if portals:
        for portal in portals:
            table = [
                ['servicename', service_status.get('servicename')],
                ['procname', portal.get('procname')],
                ['memory', portal.get('memory')],
                ['cpu', portal.get('cpu')],
                ['image', portal.get('image')],
                ['portal_numbers', len(portal.get('pods'))]
            ]
            _render_protal(table, portal, output)
    else:
        print("\tNot found, service may not been deployed.")


def _render_protal(table, portal_status, output='pretty'):
    if output == 'pretty':
        print(tabulate(table, tablefmt='psql'))
    elif output == 'json':
        print(json.dumps(portal_status))
        return
    elif output == 'json-pretty':
        print(json.dumps(portal_status, indent=2))
        return

    no_of_procs = len(portal_status.get('pods'))
    for idx, pod_status in enumerate(portal_status.get('pods'), start=1):
        if idx != no_of_procs:
            render_pod_status(pod_status)
        else:
            render_pod_status(pod_status, last_one=True)


def is_resource_instance(appname):
    if appname.find('.') == -1:
        return False
    return True


def exit_gracefully(signal, frame):
    warn("You pressed Ctrl + C, and I will exit...")
    sys.exit(130)


def git_authors(last_id, next_id):
    git_authors_cmd_format = "git show -s --format=%%aE %s...%s"
    git_authors_cmd = git_authors_cmd_format % (last_id, next_id)
    try:
        authors_str = check_output(git_authors_cmd, shell=True)
        authors = authors_str.split('\n')
        unique_authors = set()
        for author in authors:
            if author.strip(' ') == '':
                continue
            unique_authors.add(author)
        return list(unique_authors)
    except Exception:
        return []

def git_commits(last_id, next_id):
    git_commits_cmd_format = "git log --cherry-pick --right-only %s...%s '--pretty=format:%%h,%%an [%%s]'"
    git_commits_cmd = git_commits_cmd_format % (last_id, next_id)
    try:
        commits_str = check_output(git_commits_cmd, shell=True)
        commits = commits_str.split('\n')
        commits_list = []
        for cmt in commits:
            infos = cmt.split(',')
            commits_list.append({"id":infos[0], "message": ','.join(infos[1:])})
        return commits_list
    except Exception:
        return []


def git_commit_id():
    git_commit_id_cmd = 'git show -s --format=%H'
    try:
        commit_id = check_output(git_commit_id_cmd, shell=True)
        return commit_id.strip('\n')
    except Exception:
        return ""
