from sqlalchemy import Column, Integer, BigInteger, String, Text, DateTime, func
from database import Base


class SocialProfile(Base):
    __tablename__ = "social_profiles"
    __table_args__ = {"schema": "public"}

    id                       = Column(Integer, primary_key=True, index=True, autoincrement=True)
    zone                     = Column(String(200))
    party_district           = Column(String(200))
    constituency             = Column(String(200))
    designation              = Column(String(200))
    name                     = Column(String(500))
    whatsapp_number          = Column(String(50))
    dob                      = Column(String(50))
    address                  = Column(Text)
    email_id                 = Column(String(500))

    facebook_id              = Column(String(500))
    facebook_followers       = Column(BigInteger, nullable=True)
    facebook_active_status   = Column(String(50))
    facebook_verified_status = Column(String(50))

    twitter_id               = Column(String(500))
    twitter_followers        = Column(BigInteger, nullable=True)
    twitter_active_status    = Column(String(50))
    twitter_verified_status  = Column(String(50))

    instagram_id             = Column(String(500))
    instagram_followers      = Column(BigInteger, nullable=True)
    instagram_active_status  = Column(String(50))
    instagram_verified_status = Column(String(50))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
