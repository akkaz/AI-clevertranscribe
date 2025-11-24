from sqlalchemy import create_engine, Column, String, Integer, Text, JSON, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

DATABASE_URL = "sqlite:///./transcribe.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    jobs = relationship("Job", back_populates="client")

class Job(Base):
    __tablename__ = "jobs"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String)
    semantic_title = Column(String, nullable=True)  # AI-generated title
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    language = Column(String, default="it")
    model = Column(String, default="gpt-4o")
    custom_prompt = Column(Text, nullable=True)
    transcription = Column(Text, nullable=True)
    analysis_report = Column(Text, nullable=True)
    analysis_todo = Column(JSON, nullable=True) # List of dicts: [{"text": "...", "done": False}]
    error = Column(String, nullable=True)
    
    client_id = Column(String, ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", back_populates="jobs")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
