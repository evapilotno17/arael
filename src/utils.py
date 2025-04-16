from typing import List, Optional, Tuple
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from src.models import Keystroke

ANSI_KEYMAP = {
    "a": ("a", "A"), "b": ("b", "B"), "c": ("c", "C"), "d": ("d", "D"),
    "e": ("e", "E"), "f": ("f", "F"), "g": ("g", "G"), "h": ("h", "H"),
    "i": ("i", "I"), "j": ("j", "J"), "k": ("k", "K"), "l": ("l", "L"),
    "m": ("m", "M"), "n": ("n", "N"), "o": ("o", "O"), "p": ("p", "P"),
    "q": ("q", "Q"), "r": ("r", "R"), "s": ("s", "S"), "t": ("t", "T"),
    "u": ("u", "U"), "v": ("v", "V"), "w": ("w", "W"), "x": ("x", "X"),
    "y": ("y", "Y"), "z": ("z", "Z"),
    "1": ("1", "!"), "2": ("2", "@"), "3": ("3", "#"), "4": ("4", "$"),
    "5": ("5", "%"), "6": ("6", "^"), "7": ("7", "&"), "8": ("8", "*"),
    "9": ("9", "("), "0": ("0", ")"),
    "`": ("`", "~"), "-": ("-", "_"), "=": ("=", "+"),
    "[": ("[", "{"), "]": ("]", "}"), "\\": ("\\", "|"),
    ";": (";", ":"), "'": ("'", "\""), ",": (",", "<"),
    ".": (".", ">"), "/": ("/", "?"),
    "<space>": (" ", " "), "<enter>": ("\n", "\n"), "<tab>": ("\t", "\t"),
}

class Utils:
    def __init__(self, db_path: str = "sqlite:///arael.db"):
        engine = create_engine(db_path)
        Session = sessionmaker(bind=engine)
        session = Session()
        self.df = pd.read_sql(select(Keystroke), engine)[['timestamp', 'key']]
        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        self.df['date'] = self.df['timestamp'].dt.date
        self.df['hour'] = self.df['timestamp'].dt.hour
        self.df['minute'] = self.df['timestamp'].dt.minute

    def keysequence_output(self, keys: List[str]) -> str:
        result = []
        shift = False
        caps_lock = False
        for key in keys:
            k = key.lower()
            if k == "<shift>":
                shift = True
                continue
            elif k == "<caps_lock>":
                caps_lock = not caps_lock
                continue
            elif k == "<backspace>":
                if result:
                    result.pop()
                continue
            if k in ANSI_KEYMAP:
                base, shifted = ANSI_KEYMAP[k]
                if k.isalpha():
                    result.append(shifted if caps_lock ^ shift else base)
                else:
                    result.append(shifted if shift else base)
            shift = False
        return ''.join(result)

    def filter_by_day(self, day: Optional[str] = None) -> pd.DataFrame:
        if day is None:
            day = datetime.today().strftime('%Y-%m-%d')
        df = self.df.copy()
        df['date'] = df['timestamp'].dt.strftime('%Y-%m-%d')
        return df[df['date'] == day].drop(columns='date')

    def segment_into_sessions(self, df: pd.DataFrame, idle_threshold: int = 15) -> List[pd.DataFrame]:
        if df.empty:
            return []
        df = df.copy()
        df['delta'] = df['timestamp'].diff().fillna(pd.Timedelta(seconds=0))
        session_breaks = df['delta'] > timedelta(seconds=idle_threshold)
        session_ids = session_breaks.cumsum()
        return [group.drop(columns='delta') for _, group in df.groupby(session_ids)]

    def session_info(self, day: Optional[str] = None) -> List[Tuple[datetime, datetime, str]]:
        today = self.filter_by_day(day)
        segs = self.segment_into_sessions(today)
        res = []
        for seg in segs:
            if seg.shape[0] < 5:
                continue
            start, end = seg.iloc[0]['timestamp'], seg.iloc[-1]['timestamp']
            text = self.keysequence_output(list(seg['key']))
            res.append((start, end, text))
        return res

    def get_typing_speed(self, session: Tuple[datetime, datetime, str]) -> float:
        words = len(session[2].split())
        elapsed = (session[1] - session[0]).total_seconds()
        return words * 60 / elapsed if elapsed > 0 else 0

    def pretty_print_day_logs(self, day: Optional[str] = None) -> None:
        sessions = self.session_info(day)
        for start, end, text in sessions:
            speed = self.get_typing_speed((start, end, text))
            print(f"[{start.strftime('%H:%M:%S')}] typing_speed: {speed:.2f} wpm")
            print(text)
            print('-' * 60)

