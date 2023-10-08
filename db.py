from dateutil import parser
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, \
    String, DateTime, Boolean, BLOB, ForeignKey, TypeDecorator
from sqlalchemy.orm import sessionmaker, declarative_base
import numpy as np

# Define the base class for all models
Base = declarative_base()

class NumpyArray(TypeDecorator):
    """Enables storage of numpy arrays in SQLite database"""
    impl = BLOB

    cache_ok = True # enable per-instance memoized caching
    
    def process_bind_param(self, value, dialect):
        return value.tobytes() if value is not None else None
    
    def process_result_value(self, value, dialect):
        return np.frombuffer(value, dtype=np.float32).reshape(-1) if value is not None else None

class ImageEmbeddings(Base):
    """Model for storing image embeddings in database"""
    __tablename__ = 'image_embeddings'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    sha1 = Column(String)
    last_updated = Column(DateTime)
    embedding = Column(NumpyArray)

def get_session(filename):
    """Create a session to interact with the database"""
    engine = create_engine(f'sqlite:///{filename}')

    # Create the tables in the database if they do not exist
    Base.metadata.create_all(engine)

    # Create a session to interact with the database
    Session = sessionmaker(bind=engine)
    return Session()