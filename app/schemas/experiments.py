"""
Define Experiement API Schemas.
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ExperimentBase(BaseModel):
    title: str


class ExperimentRead(ExperimentBase):
    id: uuid.UUID
    live: bool
    target_col: str
    model_schema: str
    file_id: str
    date: datetime


class ExperimentCreate(ExperimentBase):
    file_id: str
    target_col: str
