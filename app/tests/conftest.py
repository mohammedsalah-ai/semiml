"""
Configuration file for pytest
"""

import pytest
import pytest_asyncio

import httpx

from asgi_lifespan import LifespanManager

from app.main import app

AUTHENTICATED_TEST_USER_EMAIL = "dr.stone@senku.com"
AUTHENTICATED_TEST_USER_PASSWORD = "#1ScienceNow"


@pytest_asyncio.fixture
async def unauth_client():
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as async_client:
            yield async_client


@pytest_asyncio.fixture
async def auth_client():
    async with LifespanManager(app):
        transport = httpx.ASGITransport(app)
        async with httpx.AsyncClient(
            transport=transport, base_url="http://testserver"
        ) as async_client:

            await async_client.post(
                "/auth/register",
                json={
                    "email": AUTHENTICATED_TEST_USER_EMAIL,
                    "password": AUTHENTICATED_TEST_USER_PASSWORD,
                },
            )

            res = await async_client.post(
                "/auth/jwt/login",
                data={
                    "username": AUTHENTICATED_TEST_USER_EMAIL,
                    "password": AUTHENTICATED_TEST_USER_PASSWORD,
                },
            )

            creds = res.json()
            token = creds["access_token"]

            async_client.headers.update({"Authorization": f"Bearer {token}"})

            yield async_client
