from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime
import pytz

Base = declarative_base()
india = pytz.timezone("Asia/Kolkata")

class Keystroke(Base):
    __tablename__ = 'keystrokes'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.now(india), index=True, nullable=False)
    key = Column(String, nullable=False)
    device = Column(String, default='laptop')
    session = Column(String, nullable=True)
