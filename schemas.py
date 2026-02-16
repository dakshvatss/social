from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime, date


class ProfileBase(BaseModel):
    zone:                      Optional[str] = None
    party_district:            Optional[str] = None
    constituency:              Optional[str] = None
    designation:               Optional[str] = None
    name:                      Optional[str] = None
    whatsapp_number:           Optional[str] = None
    dob:                       Optional[str] = None
    address:                   Optional[str] = None
    email_id:                  Optional[str] = None

    facebook_id:               Optional[str] = None
    facebook_followers:        Optional[int] = None
    facebook_active_status:    Optional[str] = None
    facebook_verified_status:  Optional[str] = None

    twitter_id:                Optional[str] = None
    twitter_followers:         Optional[int] = None
    twitter_active_status:     Optional[str] = None
    twitter_verified_status:   Optional[str] = None

    instagram_id:              Optional[str] = None
    instagram_followers:       Optional[int] = None
    instagram_active_status:   Optional[str] = None
    instagram_verified_status: Optional[str] = None

    @field_validator('dob', mode='before')
    @classmethod
    def convert_dob(cls, v):
        if isinstance(v, date) and not isinstance(v, datetime):
            return v.isoformat()
        return v


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BulkDeleteRequest(BaseModel):
    ids: list[int]
