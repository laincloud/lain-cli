# -*- coding: utf-8 -*-
import tempfile
import subprocess


def update():
    """
    Update Lain SDK and CLI
    """

    update_pkg = ['lain-cli', 'lain-sdk']
    for pkg in update_pkg:
        git_url = 'https://github.com/laincloud/%s.git' % pkg
        tmpdir = tempfile.mkdtemp()
        subprocess.check_call(['git', 'clone', '--depth', '1', git_url, tmpdir])
        cmd_setup_install = ['sudo', 'python', 'setup.py', 'install']
        subprocess.call(cmd_setup_install, cwd=tmpdir)
        subprocess.call(['sudo', 'rm', '-rf', tmpdir])
