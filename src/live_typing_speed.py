import sys, signal, numpy as np
from datetime import datetime
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

from src.db import SessionLocal      
from src.models import Keystroke

AVG_CHARS_PER_WORD = 5
ROLLING_WINDOW     = 120
QUERY_BATCH        = 30
UPDATE_INTERVAL_MS = 1000


class _TypingSpeedGrapher:
    def __init__(self):
        self.db  = SessionLocal()


        self.app = QtWidgets.QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(True)
        self.app.aboutToQuit.connect(self._cleanup)

        self.win  = pg.GraphicsLayoutWidget(show=True,
                                            title="Live TypingSpeed Monitor")
        self.win.resize(800, 400)

        self.plot = self.win.addPlot(title=" WPM (rolling)")
        self.plot.setLabel('left',   'WPM')
        self.plot.setLabel('bottom', 'seconds ago')
        self.plot.setYRange(0, 160)
        self.plot.showGrid(x=True, y=True)

        self.data  = np.zeros(ROLLING_WINDOW)
        self.curve = self.plot.plot(self.data, pen='y')

        # tick every UPDATE_INTERVAL_MS
        self.timer          = QtCore.QTimer()
        self.timer.timeout.connect(self._tick)
        self.timer.start(UPDATE_INTERVAL_MS)

        # ctrlC - close the process (although thius wont work if you're running the process through ctl)
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._sig_exit)

    def _sig_exit(self, *_):
        QtWidgets.QApplication.quit()

    def _cleanup(self):
        self.timer.stop()
        self.db.close()

    def _compute_wpm(self) -> float:
        """pull the newest QUERY_BATCH keystrokes and convert to wpm."""
        rows = (self.db.query(Keystroke.timestamp)
                       .order_by(Keystroke.timestamp.desc())
                       .limit(QUERY_BATCH)
                       .all())
        if len(rows) < 2:
            return 0.0
        newest = rows[0][0]
        oldest = rows[-1][0]
        elapsed = (newest - oldest).total_seconds()
        if elapsed <= 0:
            return 0.0
        now = datetime.now()
        elapsed_from_cur = (now - oldest).total_seconds()

        kps = len(rows) / elapsed_from_cur
        return (kps * 60) / AVG_CHARS_PER_WORD

    def _tick(self):
        wpm = self._compute_wpm()
        self.data = np.roll(self.data, -1)
        self.data[-1] = wpm
        self.curve.setData(self.data)

    def run(self):
        sys.exit(self.app.exec_())


def main():
    _TypingSpeedGrapher().run()

if __name__ == "__main__":
    main()
