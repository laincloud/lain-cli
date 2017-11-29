#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import argh
import signal

from lain_cli.attach import attach
from lain_cli.dashboard import dashboard
from lain_cli.reposit import reposit
from lain_cli.prepare import prepare
from lain_cli.build import build
from lain_cli.tag import tag
from lain_cli.push import push
from lain_cli.sync import sync
from lain_cli.deploy import deploy
from lain_cli.scale import scale
from lain_cli.ps import ps
from lain_cli.undeploy import undeploy

from lain_cli.login import login, refresh
from lain_cli.logout import logout

from lain_cli.rmi import rmi
from lain_cli.meta import meta
from lain_cli.enter import enter
from lain_cli.clear import clear
from lain_cli.imagecheck import check
from lain_cli.validate import validate
from lain_cli.appversion import appversion
from lain_cli.prepare_update import prepare_update

from lain_cli.test import test
from lain_cli.run import run, debug, stop, rm

from lain_cli.update import update
from lain_cli.version import version

from lain_cli.config import ConfigCommands
from lain_cli.secret import SecretCommands
from lain_cli.backup import BackupCommands
from lain_cli.maintainer import MaintainerCommands

from lain_cli.utils import exit_gracefully

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("docker").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


one_level_commands = [
    appversion, attach, build, check, clear, dashboard, debug,
    deploy, enter, login, logout, meta, prepare, prepare_update,
    ps, push, refresh, reposit, rm, rmi, run, sync,
    scale, stop, tag, test, undeploy, update, validate, version
]

two_level_commands = [
    ConfigCommands, SecretCommands,
    BackupCommands, MaintainerCommands,
]


def main():
    signal.signal(signal.SIGINT, exit_gracefully)
    parser = argh.ArghParser()
    parser.add_commands(one_level_commands)
    for command in two_level_commands:
        argh.add_commands(parser, command.subcommands(), namespace=command.namespace(), help=command.help_message())
    parser.dispatch()


if __name__ == "__main__":
    main()
