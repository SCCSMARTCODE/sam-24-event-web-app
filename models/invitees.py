"""
This module contains the school account -->
"""
from sqlalchemy import Column, String, Integer
from models.base_model import BaseModel, Base


class Invitees(BaseModel, Base):

        __tablename__ = "registered_invitees"
        fullname = Column(String(40), unique=True, nullable=False)
        email = Column(String(40))
        phone_address = Column(String(30), unique=True, nullable=False)
        profile_pic_file_name = Column(String(30), nullable=False)
        pass_code = Column(String(10), nullable=False, unique=True)
        table_number = Column(Integer)
        chair_number = Column(Integer, nullable=False)
        relationship_with_sam24 = Column(String(40), nullable=False)
