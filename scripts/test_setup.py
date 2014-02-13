#! /usr/bin/python
import subprocess
import sys

def _execute(cmd):
    if 0 != subprocess.call(cmd, shell=True):
        sys.exit(-1)

if __name__ == '__main__':
    deps = [
        "nose",
        "pyforge",
    ]
    if sys.version_info < (3, 0):
        try:
            import __pypy__ # No gevent on pypy
        except ImportError:
            deps.append("gevent")
    if sys.version_info < (2, 7):
        deps.append("unittest2")

    _execute("pip install --use-mirrors {0}".format(" ".join(deps)))
