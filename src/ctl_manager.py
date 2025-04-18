import argparse
import subprocess
import os
import signal
import sys
from src.models import Keystroke
from src.db import SessionLocal
from collections import defaultdict
from pathlib import Path
from src.utils import Utils
from io import StringIO

def exposed(func):
    func._is_exposed = True
    return func

class CTLManager:
    def __init__(self, path=None):
        self.PID_FILE = path or Path.home() / ".arael.pid"

    def get_pid(self):
        if self.PID_FILE.exists():
            with open(self.PID_FILE) as f:
                return int(f.read().strip())
        return None

    def is_running(self, pid):
        try:
            os.kill(pid, 0)
            return True
        except:
            return False

    @exposed
    def start(self, verbose=False):
        """
            Awken arael. --verbose : stream arael stdout/stderr
        """
        if self.PID_FILE.exists():
            pid = self.get_pid()
            if pid and self.is_running(pid):
                print(f"already running at PID {pid}")
                return
            self.PID_FILE.unlink(missing_ok=True)

        redir = None if verbose else subprocess.DEVNULL
        kl_proc = subprocess.Popen(
            [sys.executable, "-m", "src.arael"],
            stdout=redir, stderr=redir,
        )
        with open(self.PID_FILE, "w") as f:
            f.write(str(kl_proc.pid))

        print(f"arael has awakened and is watching you at (PID {kl_proc.pid})")

    @exposed
    def live(self):
        """
            monitor your typing speed live!!
        """
        pid = self.get_pid()
        if not pid or not self.is_running(pid):
            self.start()
        live_proc = subprocess.Popen(
            [sys.executable, "-m", "src.live_typing_speed"]
        )
        print(f"live typing speed monitor started (PID {live_proc.pid})")

    @exposed
    def stop(self):
        """Stop the keylogger."""
        pid = self.get_pid()
        if pid is None:
            print("Arael not running")
            return
        try:
            os.kill(pid, signal.SIGTERM)
            print("Arael stopped")
        except OSError as e:
            print("Could not kill process")
            print(e)
        finally:
            self.PID_FILE.unlink(missing_ok=True)

    @exposed
    def status(self):
        """Check if Arael is running."""
        pid = self.get_pid()
        if pid and self.is_running(pid):
            print(f"Arael is running (PID {pid})")
        else:
            print("Arael is not running")

    @exposed
    def regenerate_logs(self):
        """
            regenerate pretty-printed session logs into ./logs/.
        """
        utils = Utils()
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        days = utils.df['timestamp'].dt.strftime('%Y-%m-%d').unique()

        for day in days:
            buf = StringIO()
            sessions = utils.session_info(day)

            for start, end, text in sessions:
                if len(text.strip()) == 0:
                    continue
                speed = utils.get_typing_speed((start, end, text))
                buf.write(f"[{start.strftime('%H:%M:%S')}] typing_speed: {speed:.2f} wpm\n")
                buf.write(text + "\n" + '-' * 60 + "\n")

            with open(log_dir / f"{day}.txt", "w") as f:
                f.write(buf.getvalue())

        print(f"regenerated logs for {len(days)} day(s)")

    @exposed
    def help(self):
        """Show this help message."""
        print("\nArael CLI — Available Commands:\n")
        for name in dir(self):
            method = getattr(self, name)
            if callable(method) and getattr(method, "_is_exposed", False):
                doc = method.__doc__ or "(no description)"
                sig = "(--verbose)" if name == "start" else ""
                print(f"  {name:<10} {sig:<12} : {doc.strip()}")
        print()