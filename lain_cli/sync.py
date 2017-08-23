import requests
import lain_sdk.mydocker as docker
from lain_sdk.util import error, warn, info
from argh.decorators import arg
from lain_cli.utils import check_phase, get_domain
from lain_cli.auth import SSOAccess, get_auth_header


@arg('src_phase',  help='The source registry domain for sync from, can not be None')
@arg('dst_phase', help="lain cluster phase id, can be added by lain config save")
@arg('appname', help="app name")
@arg('meta_version', help='The Meta version of some build')
def sync(src_phase, dst_phase, appname, meta_version):
    check_phase(src_phase)
    check_phase(dst_phase)

    src_domain = get_domain(src_phase)
    dst_domain = get_domain(dst_phase)

    src_registry = "registry.{domain}".format(domain=src_domain)
    dst_registry = "registry.{domain}".format(domain=dst_domain)

    src_phase_meta_tag = docker.gen_image_name(
        appname, 'meta', meta_version, src_registry)
    src_phase_release_tag = docker.gen_image_name(
        appname, 'release', meta_version, src_registry)

    dst_phase_meta_tag = docker.gen_image_name(
        appname, 'meta', meta_version, dst_registry)
    dst_phase_release_tag = docker.gen_image_name(
        appname, 'release', meta_version, dst_registry)

    if transfer_to(src_phase_meta_tag, dst_phase_meta_tag) != 0:
        return
    if transfer_to(src_phase_release_tag, dst_phase_release_tag) != 0:
        return

    access_token = SSOAccess.get_token(dst_phase)
    auth_header = get_auth_header(access_token)
    info("notifying lain push.")
    notify_pushs(dst_domain, appname, auth_header)
    info("notify lain push done.")


def transfer_to(src_tag, dst_tag):
    if docker.pull(src_tag) != 0 or docker.tag(src_tag, dst_tag) != 0 or docker.push(dst_tag) != 0:
        return 1
    return 0


def notify_pushs(domain, appname, auth_header):
    headers = {"Content-type": "application/json"}
    headers.update(auth_header)
    url = "http://console.%s/api/v1/repos/%s/push/" % (domain, appname)
    try:
        resp = requests.request(
            "POST", url, headers=headers, timeout=10)
        datas = resp.json()
        if resp.status_code < 200 or resp.status_code >= 400:
            warn('Notify lain push failed with error: %s' %
                 datas['msg'])
    except Exception as e:
        warn('Notify lain push failed with error: %s' % e)
