from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, JSON, DateTime, ForeignKey, DOUBLE_PRECISION
from typing import Optional
from datetime import datetime

Base = declarative_base()

class Feedback(Base):
    __tablename__ = "Feedback"
    
    id: Mapped[str] = mapped_column(String, primary_key = True)    
    createdAt: Mapped[datetime] = mapped_column(DateTime)
    updatedAt: Mapped[datetime] = mapped_column(DateTime)
    stepId: Mapped[str] = mapped_column(String, ForeignKey("Step.id"))
    name: Mapped[str] = mapped_column(String)
    value: Mapped[float] = mapped_column(DOUBLE_PRECISION)
    comment: Mapped[Optional[str]] = mapped_column(String, nullable = True)
    
    step: Mapped["Step"] = relationship("Step", back_populates = "feedbacks")

class Step(Base):
    __tablename__ = "Step"
    
    id: Mapped[str] = mapped_column(String, primary_key = True)
    createdAt: Mapped[datetime] = mapped_column(DateTime)
    updatedAt: Mapped[datetime] = mapped_column(DateTime)
    parentId: Mapped[Optional[str]] = mapped_column(String, nullable = True)
    threadId: Mapped[str] = mapped_column(String, ForeignKey("Thread.id"))
    input: Mapped[str] = mapped_column(String)
    metadata: Mapped[dict] = mapped_column(JSON) 
    name: Mapped[str] = mapped_column(String)
    output: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String) 
    showInput: Mapped[str] = mapped_column(String)
    isError: Mapped[bool] = mapped_column(Boolean)
    startTime: Mapped[datetime] = mapped_column(DateTime) 
    endTime: Mapped[datetime] = mapped_column(DateTime)
    
    thread: Mapped["Thread"] = relationship("Thread", back_populates = "steps")
    feedbacks: Mapped[list["Feedback"]] = relationship("Feedback", back_populates = "step")

class Thread(Base):
    __tablename__ = "Thread"
    
    id: Mapped[str] = mapped_column(String, primary_key = True)
    createdAt: Mapped[datetime] = mapped_column(DateTime)
    updatedAt: Mapped[datetime] = mapped_column(DateTime)
    deletedAt: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable = True)
    name: Mapped[str] = mapped_column(String)
    metadata: Mapped[dict] = mapped_column(JSON)
    userId: Mapped[str] = mapped_column(String, ForeignKey("User.id"))
    tags: Mapped[str] = mapped_column(String)
    
    steps: Mapped[list["Step"]] = relationship("Step", back_populates = "thread")
    users: Mapped[list["User"]] = relationship("User", back_populates = "treads")

class Element(Base):  
    __tablename__ = "Element"  
    
    id: Mapped[str] = mapped_column(String, primary_key = True)
    createdAt: Mapped[datetime] = mapped_column(DateTime)
    updatedAt: Mapped[datetime] = mapped_column(DateTime)
    threadId: Mapped[str] = mapped_column(String, ForeignKey("Thread.id"))
    stepId: Mapped[str] = mapped_column(String, ForeignKey("Step.id"))
    metadata: Mapped[dict] = mapped_column(JSON)
    mime: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    objectKey: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)
    chainInKey: Mapped[str] = mapped_column(String)
    display: Mapped[str] = mapped_column(String)
    size: Mapped[str] = mapped_column(String)
    language: Mapped[str] = mapped_column(String)
    page: Mapped[int] = mapped_column(Integer)
    props: Mapped[dict] = mapped_column(JSON)
    
    thread: Mapped["Thread"] = relationship("Thread")
    step: Mapped["Step"] = relationship("Step")

class User(Base):
    __tablename__ = "User"

    id: Mapped[str] = mapped_column(String, primary_key = True)
    createdAt: Mapped[datetime] = mapped_column(DateTime)
    updatedAt: Mapped[datetime] = mapped_column(DateTime)
    metadata: Mapped[dict] = mapped_column(JSON)
    identifier: Mapped[str] = mapped_column(String)

    threads: Mapped[list["Thread"]] = relationship("Thread", back_populates = "users")