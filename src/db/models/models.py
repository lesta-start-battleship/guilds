from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey, Boolean, Numeric
from datetime import datetime
from sqlalchemy.orm import relationship
from models.database import Base


class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    result = Column(JSON)
    error = Column(String)
    status = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    time_processed = Column(Numeric(10, 3), default=0.000)

    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="processed_files")

    word_stats = relationship(
        "WordStat",
        back_populates="processed_file",
        foreign_keys="[WordStat.processed_file_id]"
    )
    collection_id = Column(Integer, ForeignKey("collections.id"), nullable=True)
    collection = relationship("Collection", back_populates="processed_files")


class WordStat(Base):
    __tablename__ = "word_stats"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, ForeignKey("processed_files.file_id"), index=True)
    term = Column(String, index=True)
    tf = Column(Integer)
    idf = Column(Float)

    processed_file_id = Column(Integer, ForeignKey("processed_files.id"))

    processed_file = relationship(
        "ProcessedFile",
        back_populates="word_stats",
        foreign_keys="[WordStat.processed_file_id]"
    )


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    processed_files = relationship("ProcessedFile", back_populates="owner", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="owner", cascade="all, delete-orphan")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=True) # это не нужно
    description = Column(String, nullable=True) # это не нужно
    created_at = Column(DateTime, default=datetime.utcnow)

    # Владелец коллекции
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="collections")

    # Документы в коллекции
    processed_files = relationship("ProcessedFile", back_populates="collection", cascade="all, delete-orphan")
