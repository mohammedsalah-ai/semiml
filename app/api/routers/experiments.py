"""
Define experiments routes.
"""

import asyncio
import aiofiles.os
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.orm import SessionEvents, SessionTransactionOrigin

from app.core.db import get_async_session
from app.models.users import User, current_active_user
from app.models.files import File
from app.models.experiments import Experiment
from app.schemas.experiments import ExperimentRead, ExperimentCreate

from fastapi import APIRouter

import joblib
import uuid
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

router = APIRouter()


async def run_experiment(
    data: pd.DataFrame, file: File, experiment: Experiment, session: AsyncSession
):

    schema = "Input: "

    X = data.drop(columns=[experiment.target_col])
    y = data[experiment.target_col]

    schema += ", ".join([f"{col} ({X[col].dtype})" for col in X.columns])

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    schema += " Output: "
    schema += ", ".join(
        [f"{label}={index}" for index, label in enumerate(label_encoder.classes_)]
    )

    model = RandomForestClassifier()
    model.fit(X, y_encoded)

    model_path = "/home/supermaker/models/" + experiment.title + ".pkl"
    joblib.dump(model, model_path)

    setattr(experiment, "model_path", model_path)
    setattr(experiment, "model_schema", schema)
    session.add(experiment)
    await session.commit()


async def get_experiment_or_404(
    id: uuid.UUID, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> Experiment:
    experiment = await session.get(Experiment, id)
    if not experiment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return experiment


@router.post("/", response_model=ExperimentRead)
async def create_experiment(
    user: Annotated[User, Depends(current_active_user)],
    experiment_create: ExperimentCreate,
    session: Annotated[AsyncSession, Depends(get_async_session)],
    bg: BackgroundTasks,
):
    file = await session.get(File, experiment_create.file_id)
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="ID of a non-existent file"
        )

    if user is not file.user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only owned files could be used",
        )

    data = await asyncio.to_thread(pd.read_csv, file.path)
    if experiment_create.target_col not in data.columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Target column not in file"
        )

    new_experiment = Experiment(**experiment_create.model_dump(), user=user)
    session.add(new_experiment)
    await session.commit()

    bg.add_task(run_experiment, data, file, new_experiment, session)

    return new_experiment


@router.get("/", response_model=list[ExperimentRead])
async def list_experiments(
    user: Annotated[User, Depends(current_active_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    return user.experiments


@router.get("/{id}", response_model=ExperimentRead)
async def get_experiment(
    user: Annotated[User, Depends(current_active_user)],
    experiment: Annotated[Experiment, Depends(get_experiment_or_404)],
):
    return experiment


@router.delete("/{id}")
async def delete_experiment(
    user: Annotated[User, Depends(current_active_user)],
    experiment: Annotated[Experiment, Depends(get_experiment_or_404)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if user is not experiment.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you cannot delete an experiment that is not yours!",
        )

    await aiofiles.os.remove(experiment.model_path)
    await session.delete(experiment)
    await session.commit()


@router.post("/live/{id}", response_model=ExperimentRead)
async def toggle_live(
    user: Annotated[User, Depends(current_active_user)],
    experiment: Annotated[Experiment, Depends(get_experiment_or_404)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if user is not experiment.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you cannot toggle an experiment that is not yours!",
        )

    current_status = experiment.live
    new_status = not current_status

    setattr(experiment, "live", new_status)
    session.add(experiment)
    await session.commit()

    return experiment


class ModelIn(BaseModel):
    input: list[int | float | str]


@router.post("/model/{id}")
async def predict_model(
    model_in: ModelIn,
    user: Annotated[User, Depends(current_active_user)],
    experiment: Annotated[Experiment, Depends(get_experiment_or_404)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if not experiment.live:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="experiment is not live to be used",
        )

    model = joblib.load(experiment.model_path)
    data = np.array(model_in.input).reshape(1, -1)
    res = model.predict(data)[0]

    return {"output": f"{res}"}
