# -*- coding: utf-8 -*-
import sys
import requests
import json
from argh.decorators import arg

from lain_sdk.util import error, warn, info
import lain_sdk.mydocker as docker
from lain_cli.utils import check_phase, lain_yaml, get_domain, git_authors, git_commit_id


@arg('phase', help="lain cluster phase id, can be added by lain config save")
def push(phase):
    """
    Push release and meta images
    """

    check_phase(phase)
    info("Pushing meta and release images ...")
    yml = lain_yaml(ignore_prepare=True)
    meta_version = yml.repo_meta_version()
    if meta_version is None:
        error("please git commit.")
        return None
    domain = get_domain(phase)
    registry = "registry.%s" % domain
    phase_meta_tag = docker.gen_image_name(
        yml.appname, 'meta', meta_version, registry)
    phase_release_tag = docker.gen_image_name(
        yml.appname, 'release', meta_version, registry)
    meta_code = docker.push(phase_meta_tag)
    release_code = docker.push(phase_release_tag)
    if meta_code or release_code:
        error("Error lain push.")
        sys.exit(1)
    else:
        info("Done lain push.")
        info("notifying lain push.")
        last_commit_id = fetch_last_commit_id(domain, yml.appname)
        if last_commit_id is not None:
            notify_diffs(domain, yml.appname, last_commit_id)
        else:
            warn("Notified Nothing!")
        info("Done notifying lain push.")


def fetch_last_commit_id(domain, appname):
    url = "http://console.%s/api/v1/repos/%s/details/" % (domain, appname)
    commitid_length = 40
    try:
        resp = requests.request("GET", url, timeout=10)
        datas = resp.json()
        if resp.status_code == 404:
            warn('%s' % datas['msg'])
            return None
        elif resp.status_code < 200 or resp.status_code >= 400:
            warn('Fetch lastest meta version failed with error: %s' %
                  datas['msg'])
            return None
        details = datas['detail']
        meta_version = details.get('meta_version', '')
        giturl = details.get('giturl', '')
        if giturl.strip() == '':
            warn('No Giturl Bound')
            return None
        last_commit_id = meta_version[-commitid_length:]
        return last_commit_id
    except Exception:
        # do nothing, compatible with old console versions
        pass
    return None


def notify_diffs(domain, appname, last_commit_id):
    current_git_commit = git_commit_id()
    if current_git_commit == last_commit_id:
        warn('nothing changed!')
        return
    unique_authors = git_authors(last_commit_id, 'HEAD')
    headers = {"Content-type": "application/json"}
    url = "http://console.%s/api/v1/repos/%s/push/" % (domain, appname)
    body = {'authors': unique_authors}
    try:
        resp = requests.request("POST", url, headers=headers, json=body, timeout=10)
        datas = resp.json()
        if resp.status_code < 200 or resp.status_code >= 400:
            warn('Notify lain push failed with error: %s' %
                  datas['msg'])
    except Exception as e:
        warn('Notify lain push failed with error: %s' % e)
