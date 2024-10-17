"""
Define File API Schemas.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class FileBase(BaseModel):
    title: str
    date: datetime


class FileRead(FileBase):
    id: uuid.UUID
