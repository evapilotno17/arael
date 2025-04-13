import argparse
import subprocess
import os
import signal
import sys
from src.models import Keystroke
from src.db import SessionLocal
from collections import defaultdict
from pathlib import Path
from src.ctl_manager import CTLManager



if __name__ == "__main__":
    ctl = CTLManager()

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name in dir(ctl):
        method = getattr(ctl, name)
        if callable(method) and getattr(method, "_is_exposed", False):
            sub = subparsers.add_parser(name, help=method.__doc__)
            if name == "start":
                sub.add_argument("--verbose", action="store_true")

    args = parser.parse_args()
    command = args.command
    kwargs = vars(args)
    del kwargs["command"]

    getattr(ctl, command)(**kwargs)

