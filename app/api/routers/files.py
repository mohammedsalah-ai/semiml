"""
Define files routers.
"""

import io
import os
import re
import uuid
import aiofiles
import aiofiles.os
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

import pandas as pd

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Form, File, UploadFile, status
from fastapi.responses import FileResponse

from app.core.db import get_async_session
from app.models.users import User, current_active_user
from app.models.files import File as FileModel
from app.schemas.files import FileRead

router = APIRouter()

uploadtarget = "/home/supermaker/uploaded/"


async def csv_filecheck(
    file: Annotated[
        UploadFile | None, File(description="structured data in a .csv file")
    ] = None
) -> UploadFile | None:

    if not file:
        return None

    if not str(file.filename).endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type, Only .csv files are accepted",
        )

    filename = os.path.basename(str(file.filename))

    if not re.match(r"^[a-zA-Z0-9_.-]+$", filename):
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Only alphanumeric characters, underscores, periods, and hyphens are allowed",
        )

    try:
        content = await file.read()
        content_str = io.BytesIO(content)
        df = await asyncio.to_thread(pd.read_csv, content_str)

        if df.empty:
            raise ValueError("empty csv file")

        del df
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Bad-Formatted CSV file"
        )

    await file.seek(0)
    file.filename = filename

    return file


async def get_file_or_404(
    id: uuid.UUID, session: Annotated[AsyncSession, Depends(get_async_session)]
) -> FileModel:
    file = await session.get(FileModel, id)

    if file is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return file


@router.get("/", response_model=list[FileRead])
async def list_files(user: Annotated[User, Depends(current_active_user)]):
    return user.files


@router.get("/{id}", response_model=FileRead)
async def get_file(file: Annotated[FileModel, Depends(get_file_or_404)]):
    return file


@router.get("/download/{id}")
async def download_file(
    user: Annotated[User, Depends(current_active_user)],
    file: Annotated[FileModel, Depends(get_file_or_404)],
):
    if user is file.user:
        return FileResponse(file.path)

    return {"msg": "file is not public to download"}


@router.post("/", response_model=FileRead)
async def create_file(
    user: Annotated[User, Depends(current_active_user)],
    csv_file: Annotated[UploadFile | None, Depends(csv_filecheck)],
    title: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if not csv_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Provide a CSV file"
        )

    file_path = uploadtarget + str(csv_file.filename)
    new_file = FileModel(user=user, title=title, path=file_path)
    session.add(new_file)

    async with aiofiles.open(file_path, "wb") as f:
        while content := await csv_file.read(1024):
            await f.write(content)

    await session.commit()
    return new_file


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    user: Annotated[User, Depends(current_active_user)],
    file: Annotated[FileModel, Depends(get_file_or_404)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    if user is not file.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you cannot delete a file that is not yours!",
        )

    await aiofiles.os.remove(file.path)
    await session.delete(file)
    await session.commit()


@router.patch("/{id}", response_model=FileRead)
async def patch_file(
    user: Annotated[User, Depends(current_active_user)],
    file: Annotated[FileModel, Depends(get_file_or_404)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    csv_file: Annotated[UploadFile | None, Depends(csv_filecheck)],
    title: Annotated[str | None, Form()] = None,
):
    if user is not file.user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="you cannot modify a file that is not yours!",
        )

    if title:
        setattr(file, "title", title)

    if csv_file:
        await aiofiles.os.remove(file.path)

        file_path = uploadtarget + str(csv_file.filename)
        setattr(file, "path", file_path)
        async with aiofiles.open(file_path, "wb") as f:
            while content := await csv_file.read(1024):
                await f.write(content)

    session.add(file)
    await session.commit()

    return file
