from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    item_type = Column(String)
    description = Column(String, default="")
    tags = Column(String, default="")  # comma-separated
    image_path = Column(String, default="")
    available = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    nfc_tag_id = Column(String, nullable=True)
    fit = Column(String, default="")
    aesthetic = Column(String, default="")
    tone = Column(String, default="")
    layer = Column(String, default="")
    season = Column(String, default="")
    color = Column(String, default="")
    pattern_style = Column(String, default="")
    material = Column(String, default="")
    gender_expression = Column(String, default="")
    formality = Column(String, default="")
    use_case = Column(String, default="")
