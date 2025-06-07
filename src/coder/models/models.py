from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Integer, JSON, DateTime, ForeignKey, DOUBLE_PRECISION, Enum as SQLEnum, Numeric
from typing import Optional
from datetime import datetime
from enum import Enum


Base = declarative_base()

class SubTypes(Base):
    __tablename__ = "SubTypes"

    id: Mapped[int] = mapped_column(Integer, primary_key = True) 
    title: Mapped[str] = mapped_column(String) #mothly or yearly
    cost: Mapped[float] = mapped_column(Numeric)
    
    subs: Mapped["Subscription"] = relationship("Subscriptions", back_populates = "sub_types")


class Subscription(Base):
    __tablename__ = "Subscriptions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key = True)
    user_id: Mapped[str] = mapped_column(String)
    sub_type_id: Mapped[str] = mapped_column(String, ForeignKey("SubTypes.id"))
    payment_id: Mapped[str] = mapped_column(String, ForeignKey("Payments.id"))
    starts_at: Mapped[datetime] = mapped_column(DateTime, default = datetime)
    ends_at: Mapped[datetime] = mapped_column(DateTime, default = datetime)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default = True)
    
    sub_types: Mapped["SubTypes"] = relationship("SubTypes", back_populates = "subs")
    payments: Mapped["Payment"] = relationship("Payments", back_populates = "subscription")


class Payment(Base):
    __tablename__ = "Payments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key = True)
    amount: Mapped[Numeric] = mapped_column(Numeric(10,2))
    operation_id: Mapped[str] = mapped_column(String(100))
    
    subscription: Mapped["Subscription"] = relationship(back_populates = "payments")


