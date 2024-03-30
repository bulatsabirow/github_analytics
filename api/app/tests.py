import pytest
from fastapi import status


class TestRepositoriesListAPIView:
    async def test_list_repositories_retrieve(self, client):
        response = await client.get("/api/repos/top100")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 100
