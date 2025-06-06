from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, JSON, DateTime, ForeignKey, DOUBLE_PRECISION, Enum
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum

class StepType(PyEnum):
    ASSISTANT_MESSAGE = "assistant_message"
    EMBEDDING = "embedding"
    LLM = "llm"
    RETRIEVAL = "retrieval"
    RERANK = "rerank"
    RUN = "run"
    SYSTEM_MESSAGE = "system_message"
    TOOL = "tool"
    UNDEFINED = "undefined"
    USER_MESSAGE = "user_message"

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "Feedback"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)    
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    stepId: Mapped[Optional[str]] = mapped_column(String, ForeignKey("Step.id"), nullable=True)
    name: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(DOUBLE_PRECISION)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    step: Mapped["Step"] = relationship("Step", back_populates="feedbacks")

class Step(Base):
    __tablename__ = "Step"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    parentId: Mapped[Optional[str]] = mapped_column(String, ForeignKey("Step.id"), nullable=True)
    threadId: Mapped[Optional[str]] = mapped_column(String, ForeignKey("Thread.id"), nullable=True)
    input: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict) 
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    output: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    type: Mapped[StepType] = mapped_column(Enum(StepType)) 
    showInput: Mapped[Optional[str]] = mapped_column(String, default="json", nullable=True)
    isError: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    startTime: Mapped[datetime] = mapped_column(DateTime) 
    endTime: Mapped[datetime] = mapped_column(DateTime)
    
    thread: Mapped[Optional["Thread"]] = relationship("Thread", back_populates="steps")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates="step")
    elements: Mapped[list["Element"]] = relationship("Element", back_populates="step")
    parent: Mapped[Optional["Step"]] = relationship("Step", remote_side=[id], back_populates="children")
    children: Mapped[list["Step"]] = relationship("Step", back_populates="parent")

class Thread(Base):
    __tablename__ = "Thread"
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deletedAt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    userId: Mapped[Optional[str]] = mapped_column(String, ForeignKey("User.id"), nullable=True)
    
    steps: Mapped[list["Step"]] = relationship("Step", back_populates="thread")
    elements: Mapped[list["Element"]] = relationship("Element", back_populates="thread")
    user: Mapped[Optional["User"]] = relationship("User", back_populates="threads")


class Element(Base):  
    __tablename__ = "Element"  
    
    id: Mapped[str] = mapped_column(String, primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    threadId: Mapped[Optional[str]] = mapped_column(String, ForeignKey("Thread.id"), nullable=True)
    stepId: Mapped[str] = mapped_column(String, ForeignKey("Step.id"))
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    mime: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    name: Mapped[str] = mapped_column(String)
    objectKey: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    chainlitKey: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    display: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    language: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    page: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    props: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    
    thread: Mapped[Optional["Thread"]] = relationship("Thread", back_populates="elements")
    step: Mapped["Step"] = relationship("Step", back_populates="elements")

class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    createdAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updatedAt: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    identifier: Mapped[str] = mapped_column(String)

    threads: Mapped[list["Thread"]] = relationship("Thread", back_populates="user")
