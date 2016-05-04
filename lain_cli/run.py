# -*- coding: utf-8 -*-
import os
from sys import exit
from argh.decorators import arg

import lain_sdk.mydocker as docker
from lain_sdk.util import error, info
from lain_sdk.yaml.conf import DOCKER_APP_ROOT
from lain_cli.utils import lain_yaml


LOCAL_VOLUME_BASE = "/tmp/lain/run"


def gen_run_ctx(proc_name):
    yml = lain_yaml(ignore_prepare=True)
    proc = yml.procs.get(proc_name, None)
    if proc is None:
        error('proc {} does not exist'.format(proc_name))
        exit(1)
    container_name = "{}.{}.{}".format(yml.appname, proc.type.name, proc.name)
    image = yml.img_names['release']
    port = proc.port.keys()[0] if proc.port.keys() else None
    working_dir = proc.working_dir or DOCKER_APP_ROOT
    cmd = proc.cmd
    env = proc.env
    extra_env = [
        'TZ=Asia/Shanghai',
        'LAIN_APPNAME={}'.format(yml.appname),
        'LAIN_PROCNAME={}'.format(proc.name),
        'LAIN_DOMAIN=lain.local',
        'DEPLOYD_POD_INSTANCE_NO=1',
        'DEPLOYD_POD_NAME={}'.format(container_name),
        'DEPLOYD_POD_NAMESPACE={}'.format(yml.appname)
    ]
    volumes = {}
    local_proc_volume_base = os.path.join(LOCAL_VOLUME_BASE, container_name)
    if proc.volumes:
        for v in proc.volumes:
            container_path = os.path.join(local_proc_volume_base, v)
            host_path = local_proc_volume_base + container_path
            volumes[host_path] = container_path
    return container_name, image, working_dir, port, cmd, env + extra_env, volumes, local_proc_volume_base


@arg('proc_name')
def run(proc_name):
    """
    Run proc instance in the local host
    """

    container_name, image, working_dir, port, cmd, envs, volumes, _ = gen_run_ctx(proc_name)
    docker.proc_run(container_name, image, working_dir, port, cmd, envs, volumes)
    info("container name: {}".format(container_name))
    if port:
        docker.inspect_port(container_name)


@arg('proc_name')
def debug(proc_name):
    """
    Debug proc instance in the local host
    """

    container_name, _, _, _, _, _, _, _ = gen_run_ctx(proc_name)
    docker.proc_debug(container_name)


@arg('proc_name')
def stop(proc_name):
    """
    Stop proc instance in the local host
    """

    container_name, _, _, _, _, _, _, _ = gen_run_ctx(proc_name)
    docker.proc_stop(container_name)


@arg('proc_name')
def rm(proc_name):
    """
    Remove proc instance in the local host
    """

    container_name, _, _, _, _, _, _, local_proc_volume_base = gen_run_ctx(proc_name)
    docker.proc_rm(container_name, local_proc_volume_base)
