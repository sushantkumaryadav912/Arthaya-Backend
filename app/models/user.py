from sqlalchemy import Column, String, DateTime
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String(50), primary_key=True, index=True)
    firebase_uid = Column(String(128), unique=True, index=True, nullable=True)
    google_id = Column(String(128), unique=True, index=True, nullable=True)
    github_id = Column(String(128), unique=True, index=True, nullable=True)
    provider = Column(String(50), nullable=False, default="firebase") # firebase, google, github, dev, email
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    display_name = Column(String(255), nullable=True)
    organization = Column(String(255), nullable=True)
    photo_url = Column(String(500), nullable=True)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
