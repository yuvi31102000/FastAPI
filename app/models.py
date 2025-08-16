from .database import Base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, text, ForeignKey


class Post(Base):                            # Extending the Base class to create a model
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(50), nullable=False)
    content = Column(String(50), nullable=False)
    published = Column(Boolean, server_default="1", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete= "CASCADE"), nullable=False)

    user = relationship("User")  # Establishing a relationship with the User model. This allows us to access the user who created the post.


class User(Base):                           
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    phone_number = Column(String(20), nullable=False)


class Like(Base):
    __tablename__ = "likes"

    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"),primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),primary_key=True)
    liked_at = Column(TIMESTAMP(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
