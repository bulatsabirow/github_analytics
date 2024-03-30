import pytest
from fastapi import status

from app.factories import TestRepositoryFactory


class TestRepositoriesListAPIView:
    async def test_list_repositories_retrieve(self, client, test_session):
        await TestRepositoryFactory(test_session).batch_create(100)
        response = await client.get("/api/repos/top100")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 100

    async def test_list_repositories_sql_injection_prevention(self, client, test_session):
        await TestRepositoryFactory(test_session).batch_create(100)
        response = await client.get("/api/repos/top100?sort=stars; DROP TABLE repositories&sort=desc")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
