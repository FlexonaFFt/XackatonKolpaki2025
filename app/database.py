from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    who_is_user = Column(String, default="user", nullable=False)
    telegram_id = Column(String, nullable=True)  
    
    likes = relationship("UserLike", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=datetime.utcnow)
    category = Column(Integer, nullable=True)
    type = Column(String, default="post", nullable=False) 
    author_username = Column(String, nullable=True) 
    
    likes = relationship("UserLike", back_populates="post")

class UserLike(Base):
    __tablename__ = "user_likes"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

# Add this model if it doesn't exist
class PendingPost(Base):
    __tablename__ = "pending_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    author_username = Column(String, ForeignKey("users.username"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    author = relationship("User", back_populates="pending_posts")

# Добавьте это отношение в класс User
User.pending_posts = relationship("PendingPost", back_populates="author")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)