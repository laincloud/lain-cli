# -*- coding: utf-8 -*-

import os
import subprocess
import sys
from argh.decorators import arg
from jinja2 import Environment, PackageLoader
from lain_sdk.util import error, info

TEMPLATE_CHOICES = ["go", "java", "python"]
env = Environment(loader=PackageLoader("lain_cli", "templates"))


@arg("appname", help="the name of the new LAIN app")
@arg("-t", "--template", choices=TEMPLATE_CHOICES, help="template to use")
def new(appname, template="go"):
    """
    Create a LAIN project with template
    """
    if appname == "":
        error("appname should not be \"\".")
        sys.exit(1)

    try:
        if template == "go":
            new_go_project(appname)
        elif template == "java":
            new_java_project(appname)
        elif template == "python":
            new_python_project(appname)
        else:
            error("template should in {}.".format(TEMPLATE_CHOICES))
            sys.exit(1)
    except Exception as e:
        error("{}.".format(e))
        sys.exit(1)


def new_go_project(appname):
    info("Creating {} with go template...".format(appname))
    GOPATH = os.environ["GOPATH"]
    GO_SRC_PATH = "{}/src/".format(GOPATH)
    CWD = os.getcwd()
    if not CWD.startswith(GO_SRC_PATH):
        raise Exception("currenct working directory: {} is not in GOPATH: {}".
                        format(CWD, GOPATH))

    if os.path.exists(appname):
        raise Exception("directory or file: {} already exists".format(appname))

    info("`git init {}` ...".format(appname))
    subprocess.run(["git", "init", appname], check=True)
    info("`git init {}` done.".format(appname))

    with open("{}/lain.yaml".format(appname), "w+") as f:
        data = env.get_template("go/lain.yaml.j2").render(
            appname=appname, package_path=CWD.replace(GO_SRC_PATH, ""))
        f.write(data)

    with open("{}/main.go".format(appname), "w+") as f:
        data = env.get_template("go/main.go").render()
        f.write(data)

    with open("{}/Gopkg.lock".format(appname), "w+") as f:
        data = env.get_template("go/Gopkg.lock").render()
        f.write(data)

    with open("{}/Gopkg.toml".format(appname), "w+") as f:
        data = env.get_template("go/Gopkg.toml").render()
        f.write(data)

    info("`git commit` ...")
    os.chdir(appname)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run([
        "git", "-c", "user.name=LAIN", "-c", "user.email=\"\"", "commit", "-m",
        "initial commit"
    ],
                   check=True)
    os.chdir(CWD)
    info("`git commit` done.")

    info("{} has been created with go template.".format(appname))


def new_java_project(appname):
    info("Creating java project...")
    info("Java project has been created.")


def new_python_project(appname):
    info("Creating python project...")
    info("Python project has been created.")
