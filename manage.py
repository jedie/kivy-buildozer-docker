#!/usr/bin/env python3

import sys

if sys.version_info < (3,):
    print("\nERROR: Python 3 is required!\n")
    sys.exit(101)

import os
import argparse
import tempfile
import subprocess
import logging


log = logging.getLogger(__name__)


__version__ = "0.1.0"

DEFAULT_LOG_LEVEL = 20
DEFAULT_IMAGE = "jedie/buildozer"
DEFAULT_TAG = "latest"
DEFAULT_HOME = os.environ.get("HOME", "/")


class DockerUserHelper:
    def __init__(self, home):
        self.home = home
        log.info("Docker user home path: %r", home)

        self.username=os.getlogin()
        log.info("Username: %r", self.username)

        self.uid=os.getuid()
        log.info("UID: %r", self.uid)

        self.gid=os.getgid()
        log.info("GID: %r", self.gid)

        self.passwd_temp = self.make_passwd_temp()
        log.debug("Use passwd temp file: %r", self.passwd_temp.name)

        self.group_temp = self.make_group_temp()
        log.debug("Use group temp file: %r", self.group_temp.name)

    def make_passwd_temp(self):
        passwd_content="{username}:x:{uid}:{gid}:{username},,,:{home}:/bin/bash".format(
            username=self.username,
            uid=self.uid,
            gid=self.gid,
            home=self.home
        )
        log.info("passwd temp file content: %r", passwd_content)

        passwd_temp = tempfile.NamedTemporaryFile(prefix="passwd_")
        passwd_temp.write(bytes(passwd_content, encoding="utf-8"))
        passwd_temp.flush()
        return passwd_temp

    def make_group_temp(self):
        group_content="{username}:x:{gid}:".format(
            username=self.username,
            gid=self.gid,
        )
        log.info("group temp file content: %r", group_content)

        group_temp = tempfile.NamedTemporaryFile(prefix="group_")
        group_temp.write(bytes(group_content, encoding="utf-8"))
        group_temp.flush()
        return group_temp

    def get_change_user_parameters(self):
        assert os.path.isfile(self.passwd_temp.name)
        assert os.path.isfile(self.group_temp.name)
        return (
            "-v", "%s:/etc/passwd:ro" % self.passwd_temp.name,
            "-v", "%s:/etc/group:ro" % self.group_temp.name,
            "-u=%s:%s" % (self.uid, self.gid),
        )


def verbose_check(*args):
    """ "verbose" version of subprocess.check_call() """
    log.info("Call: %r", " ".join(args))
    print()
    subprocess.check_call(args, universal_newlines=True)
    print()


class DockerHelper:
    def __init__(self, image, extra_args=None):
        self.image = image
        if extra_args is None:
            self.extra_args = ()
        else:
            self.extra_args = extra_args

    def run(self, *args, extra_args=None):
        subprocess_args = ("docker", "run")
        if extra_args is not None:
            subprocess_args += extra_args
        subprocess_args += self.extra_args
        subprocess_args += (self.image,)
        subprocess_args += args

        verbose_check(*subprocess_args)


class DockerRun:
    def __init__(self, args):
        self.user_helper = DockerUserHelper(
            home=args.home
        )
        self.docker_cmd = DockerHelper(
            image="%s:%s" % (args.image, args.tag),
            extra_args=self.user_helper.get_change_user_parameters(),
        )
        
    def run(self, *args, extra_args=None):
        self.docker_cmd.run(*args, extra_args=extra_args)


def command_version_info(args):
    """
    ./manage.py version_info
    """
    docker_run = DockerRun(args)
    docker_run.run("uname", "-a")
    docker_run.run("python", "--version")
    docker_run.run("pip", "freeze")
    docker_run.run("cython", "--version")
    docker_run.run("buildozer", "--version")


def command_shell(args):
    """
    ./manage.py shell
    """
    docker_run = DockerRun(args)
    docker_run.run("bash", extra_args=("-it",))


def command_pull(args):
    """
    ./manage.py pull
    """
    verbose_check("docker", "pull", "%s:%s" % (args.image, args.tag))


def command_build(args):
    """
    ./manage.py build
    """
    verbose_check("docker", "build", "-t", args.image)


def cli():
    """
    The Commandline interface
    """

    prog = os.path.split(__file__)[-1]

    print("\n%s v%s by Jens Diemer\n" % (prog, __version__))

    # Create argument parser:

    parser = argparse.ArgumentParser(prog=prog,
        description="Build/use kivy/buildozer docker image",
    )
    parser.add_argument(
        "--version", action="version", version=__version__
    )

    # Add config arguments:

    parser.add_argument(
        "--image", default=DEFAULT_IMAGE,
        help="Docker image name (default: %r)" % DEFAULT_IMAGE
    )
    parser.add_argument(
        "--tag", default=DEFAULT_TAG,
        help="Docker image tag (default: %r)" % DEFAULT_TAG
    )
    parser.add_argument(
        "--home", default=DEFAULT_HOME,
        help=(
            "User home directory in docker container."
            " (Default: %r)"
        ) % DEFAULT_HOME
    )
    parser.add_argument(
        "--verbose", "-v", default=DEFAULT_LOG_LEVEL,
        help=(
            "Verbose Level (default:%s)"
            " CRITICAL:50,"
            " ERROR:40,"
            " WARNING:30,"
            " INFO:20,"
            " DEBUG:10,"
            " NOTSET:0"
        ) % DEFAULT_LOG_LEVEL
    )

    # Add sub commands to parser:

    subparsers = parser.add_subparsers(
        title="commands",
        description="valid sub commands are:"
    )

    #
    # ./manage.py version_info
    #
    cmd_version_info = subparsers.add_parser("version_info",
        help="print some version information from docker container"
    )
    cmd_version_info.set_defaults(func=command_version_info)
    # cmd_version_info.add_argument("name", help="package to print sha of")

    #
    # ./manage.py shell
    #
    cmd_shell = subparsers.add_parser("shell", help="Go into container bash shell")
    cmd_shell.set_defaults(func=command_shell)

    #
    # ./manage.py pull
    #
    cmd_pull = subparsers.add_parser("pull", help="Pull docker image")
    cmd_pull.set_defaults(func=command_pull)

    #
    # ./manage.py build
    #
    cmd_build = subparsers.add_parser("build", help="Build docker image")
    cmd_build.set_defaults(func=command_build)

    # parse arguments:

    args = parser.parse_args()

    if not hasattr(args, "func"):
        print("\nERROR no sub command given!\n")
        parser.print_help()
        sys.exit(-1)

    # setup logging:

    logging.basicConfig(
        level=args.verbose,
        format="%(asctime)s %(levelname)-7s %(message)s"
    )
    log.info("Set log level to: %r", args.verbose)

    # call sub command functions:

    try:
        args.func(args)
    except subprocess.CalledProcessError as err:
        print()
        log.error("subprocess error: %s", err)
        sys.exit(err.returncode)
    print()


if __name__ == "__main__":
    cli()