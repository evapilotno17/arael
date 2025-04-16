from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Base
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
db_file = project_root / "arael.db"
DB_PATH = f"sqlite:///{db_file}"

engine = create_engine(DB_PATH, echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)