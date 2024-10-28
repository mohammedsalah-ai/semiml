"""
Basic testing for application users endpoints
"""

import pytest

import httpx

from fastapi import status


@pytest.mark.asyncio
async def test_users_me(auth_client: httpx.AsyncClient):
    res = await auth_client.get("/users/me")
    assert res.status_code == status.HTTP_200_OK

    info = res.json()

    assert info["email"] == "dr.stone@senku.com"
