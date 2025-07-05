from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
from config import DATABASE_URL

Base = declarative_base()

class UserType(enum.Enum):
    CLIENT = "client"
    FREELANCER = "freelancer"
    BOTH = "both"

class OrderStatus(enum.Enum):
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DISPUTE = "dispute"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(50))
    first_name = Column(String(100))
    last_name = Column(String(100))
    user_type = Column(Enum(UserType), default=UserType.CLIENT)
    phone = Column(String(20))
    email = Column(String(100))
    bio = Column(Text)
    skills = Column(Text)  # JSON string
    portfolio_url = Column(String(200))
    rating = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    completed_orders = Column(Integer, default=0)
    total_earned = Column(Float, default=0.0)
    total_spent = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    is_banned = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    language = Column(String(10), default='ru')
    timezone = Column(String(50), default='UTC')
    
    # Relationships
    orders = relationship("Order", back_populates="client", foreign_keys='Order.client_id')
    bids = relationship("Bid", back_populates="freelancer")
    reviews_given = relationship("Review", back_populates="reviewer", foreign_keys='Review.reviewer_id')
    reviews_received = relationship("Review", back_populates="reviewee", foreign_keys='Review.reviewee_id')
    sent_messages = relationship("Message", back_populates="sender", foreign_keys='Message.sender_id')
    received_messages = relationship("Message", back_populates="receiver", foreign_keys='Message.receiver_id')

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    freelancer_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(100), nullable=False)
    budget_min = Column(Float)
    budget_max = Column(Float)
    currency = Column(String(3), default='USD')
    deadline = Column(DateTime)
    status = Column(Enum(OrderStatus), default=OrderStatus.ACTIVE)
    files = Column(Text)  # JSON string with file paths
    requirements = Column(Text)
    is_urgent = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    client = relationship("User", back_populates="orders", foreign_keys=[client_id])
    freelancer = relationship("User", foreign_keys=[freelancer_id])
    bids = relationship("Bid", back_populates="order")
    reviews = relationship("Review", back_populates="order")
    messages = relationship("Message", back_populates="order")

class Bid(Base):
    __tablename__ = 'bids'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    freelancer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    delivery_time = Column(Integer)  # in days
    message = Column(Text)
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="bids")
    freelancer = relationship("User", back_populates="bids")

class Review(Base):
    __tablename__ = 'reviews'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    reviewer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    reviewee_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="reviews")
    reviewer = relationship("User", back_populates="reviews_given", foreign_keys=[reviewer_id])
    reviewee = relationship("User", back_populates="reviews_received", foreign_keys=[reviewee_id])

class Message(Base):
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    files = Column(Text)  # JSON string with file paths
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order", back_populates="messages")
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])

class Notification(Base):
    __tablename__ = 'notifications'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50))  # new_order, new_bid, message, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    from_user_id = Column(Integer, ForeignKey('users.id'))
    to_user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default='USD')
    transaction_type = Column(String(50))  # payment, refund, commission
    status = Column(String(50), default='pending')  # pending, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    order = relationship("Order")
    from_user = relationship("User", foreign_keys=[from_user_id])
    to_user = relationship("User", foreign_keys=[to_user_id])

# Database connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()