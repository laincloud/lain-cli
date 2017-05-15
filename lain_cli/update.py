# -*- coding: utf-8 -*-
import subprocess


def update():
    """
    Update Lain SDK and CLI
    """

    update_url = 'git+https://github.com/laincloud/{}.git'
    update_pkgs = ['entry', 'lain-cli', 'lain-sdk']
    for pkg in update_pkgs:
        cmd = ['sudo', 'pip', 'install', '--process-dependency-links', update_url.format(pkg)]
        subprocess.call(cmd)
