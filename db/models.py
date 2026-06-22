from operator import ge

from sqlalchemy import (
    Column, Integer, String,
    Float, Boolean, ForeignKey,
    DateTime, Text
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    slips = relationship(
        "GrocerySlip",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    chat_history = relationship(
        "ChatHistory",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"

class GrocerySlip(Base):
    __tablename__ = "grocery_slips"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    month = Column(String, nullable=False)
    store_name = Column(String, default="Unknown")
    slip_date = Column(String, default="")
    total_amount = Column(Float, default=0.0)
    image_path = Column(Text, default="")
    notes = Column(Text, default="")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow,
                          onupdate=datetime.utcnow)

    user = relationship("User", back_populates="slips")
    items = relationship(
        "GroceryItem",
        back_populates="slip",
        cascade="all, delete-orphan"
    )
    def __repr__(self):
        return f"<GrocerySlip {self.month} total={self.total_amount}>"

class GroceryItem(Base):
    __tablename__ = "grocery_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    slip_id = Column(Integer, ForeignKey("grocery_slips.id"),
                         nullable=False)
    name = Column(String, nullable=False)
    quantity = Column(Float, default=1.0)
    unit = Column(String, default="pcs")
    unit_price = Column(Float, default=0.0)
    total_price = Column(Float, default=0.0)
    category = Column(String, default="General")
    brand = Column(String, default="")
    created_at = Column(DateTime, default=datetime.utcnow)

    slip = relationship("GrocerySlip", back_populates="items")

    def __repr__(self):
        return f"<GroceryItem {self.name} price={self.unit_price}>"

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, autoincrement=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    thread_id = Column(String, nullable=False)

    role = Column(String, nullable=False) # "user" or "bot"

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chat_history")

    def __repr__(self):
        return (
            f"<ChatHistory "
            f"user={self.user_id} "
            f"role={self.role} "
            f"msg={self.content[:30]}>"
        )
