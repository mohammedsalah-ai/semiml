"""
Define file API schemas

schemas to be used to interact with the files table in the database
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class FileBase(BaseModel):
    """defines the base schema fields for a file instance"""

    title: str
    date: datetime


class FileRead(FileBase):
    """defines the GET schema for a file instance"""

    id: uuid.UUID
