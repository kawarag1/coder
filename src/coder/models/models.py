from typing import List, Optional
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Numeric
from datetime import datetime


from sqlalchemy import String, Boolean, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    identifier: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    user_metadata: Mapped[str] = mapped_column("metadata" ,JSONB, nullable=False)
    createdAt: Mapped[Optional[str]] = mapped_column(Text)

    threads: Mapped[List["Thread"]] = relationship(back_populates="user")
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates = "user")

class Thread(Base):
    __tablename__ = "threads"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    createdAt: Mapped[Optional[str]] = mapped_column(Text)
    name: Mapped[Optional[str]] = mapped_column(String)
    userId: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    userIdentifier: Mapped[Optional[str]] = mapped_column(String)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    thread_metadata: Mapped[Optional[str]] = mapped_column("metadata", JSONB)

    user: Mapped[Optional["User"]] = relationship(back_populates="threads")
    steps: Mapped[List["Step"]] = relationship(back_populates="thread")
    elements: Mapped[List["Element"]] = relationship(back_populates="thread")
    feedbacks: Mapped[List["Feedback"]] = relationship(back_populates="thread")

class Step(Base):
    __tablename__ = "steps"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    threadId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    parentId: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("steps.id"))
    streaming: Mapped[bool] = mapped_column(Boolean, nullable=False)
    waitForAnswer: Mapped[Optional[bool]] = mapped_column(Boolean)
    isError: Mapped[Optional[bool]] = mapped_column(Boolean)
    step_metadata: Mapped[Optional[str]] = mapped_column("metadata", JSONB)
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))
    input: Mapped[Optional[str]] = mapped_column(Text)
    output: Mapped[Optional[str]] = mapped_column(Text)
    createdAt: Mapped[Optional[str]] = mapped_column(Text)
    command: Mapped[Optional[str]] = mapped_column(String)
    start: Mapped[Optional[str]] = mapped_column(Text)
    end: Mapped[Optional[str]] = mapped_column(Text)
    generation: Mapped[Optional[str]] = mapped_column(JSONB)
    showInput: Mapped[Optional[str]] = mapped_column(String)
    language: Mapped[Optional[str]] = mapped_column(String)
    indent: Mapped[Optional[int]] = mapped_column(Integer)
    defaultOpen: Mapped[bool] = mapped_column(Boolean, default = False, nullable=False)

    thread: Mapped["Thread"] = relationship(back_populates="steps")
    parent: Mapped[Optional["Step"]] = relationship(remote_side=[id])
    elements: Mapped[List["Element"]] = relationship(back_populates="step")

class Element(Base):
    __tablename__ = "elements"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    threadId: Mapped[Optional[UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"))
    type: Mapped[Optional[str]] = mapped_column(String)
    url: Mapped[Optional[str]] = mapped_column(Text)
    chainlitKey: Mapped[Optional[str]] = mapped_column(String)
    name: Mapped[str] = mapped_column(String, nullable=False)
    display: Mapped[Optional[str]] = mapped_column(String)
    objectKey: Mapped[Optional[str]] = mapped_column(String)
    size: Mapped[Optional[str]] = mapped_column(String)
    page: Mapped[Optional[int]] = mapped_column(Integer)
    language: Mapped[Optional[str]] = mapped_column(String)
    forId: Mapped[Optional[UUID]] = mapped_column(UUID, ForeignKey("steps.id"))
    mime: Mapped[Optional[str]] = mapped_column(String)
    props: Mapped[Optional[str]] = mapped_column(JSONB)

    thread: Mapped[Optional["Thread"]] = relationship(back_populates="elements")
    step: Mapped[Optional["Step"]] = relationship(back_populates="elements")

class Feedback(Base):
    __tablename__ = "feedbacks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    forId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    threadId: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text)

    thread: Mapped["Thread"] = relationship(back_populates="feedbacks")
    


class SubTypes(Base):
    __tablename__ = "SubTypes"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid4) 
    title: Mapped[str] = mapped_column(String)
    cost: Mapped[float] = mapped_column(Numeric)
    
    subs: Mapped["Subscription"] = relationship("Subscription", back_populates = "sub_types")


class Subscription(Base):
    __tablename__ = "Subscription"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid = True), primary_key = True, default = uuid4)
    userId: Mapped[str] = mapped_column(UUID, ForeignKey("users.id"))
    subTypeId: Mapped[str] = mapped_column(UUID, ForeignKey("SubTypes.id"))
    paymentId: Mapped[str] = mapped_column(UUID, ForeignKey("Payments.id"))
    startsAt: Mapped[datetime] = mapped_column(DateTime, default = datetime)
    endsAt: Mapped[datetime] = mapped_column(DateTime, default = datetime)
    autoRenew: Mapped[bool] = mapped_column(Boolean, default = True)
    
    user: Mapped["User"] = relationship("User", back_populates = "subscription")
    sub_types: Mapped["SubTypes"] = relationship("SubTypes", back_populates = "subs")
    payments: Mapped["Payment"] = relationship("Payment", back_populates = "subscription")


class Payment(Base):
    __tablename__ = "Payments"
    
    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key = True, default = uuid4)
    amount: Mapped[Numeric] = mapped_column(Numeric(10,2))
    operationId: Mapped[str] = mapped_column(String(100))
    
    subscription: Mapped["Subscription"] = relationship("Subscription", back_populates = "payments")


