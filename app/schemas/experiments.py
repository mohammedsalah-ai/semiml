"""
Define experiment API schemas

schemas to be used to interact with the experiments table in the database
"""

import uuid
from datetime import datetime
from pydantic import BaseModel, Field


class ExperimentBase(BaseModel):
    """defines the base schema fields for an experiment instance"""

    title: str


class ExperimentRead(ExperimentBase):
    """defines the GET schema for an experiment instance"""

    id: uuid.UUID
    live: bool
    target_col: str
    model_schema: str
    file_id: str
    date: datetime


class ExperimentCreate(ExperimentBase):
    """defines the POST schema for an experiment instance"""

    file_id: str
    target_col: str
