import random

from faker import Faker
from fastapi import status

from app.enums import ErrorCodes
from app.tests.factories import RepositoryFactory, RepositoryAnalyticsFactory
from app.tests.schema import RepositoryAnalyticsSortingQueryParamsTest

fake = Faker()


class TestRepositoriesListAPIView:
    async def test_list_repositories(self, client, test_session):
        # TODO use named urls
        await RepositoryFactory(test_session).create_batch(100)
        response = await client.get("/api/repos/top100")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 100

    async def test_list_repositories_sql_injection_prevention(self, client, test_session):
        await RepositoryFactory(test_session).create_batch(100)
        response = await client.get("/api/repos/top100?sort=stars; DROP TABLE repositories&sort=desc")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestRepositoryAnalyticsRetrieveAPIView:
    async def test_analytics_retrieve(self, client, test_session):
        repositories = await RepositoryFactory(test_session).create_batch(100)
        repository = random.choice(repositories)
        owner, repo = repository["repo"].split("/")
        repos_analytics = await RepositoryAnalyticsFactory(test_session).create_batch(1000)
        dummy_query_params = RepositoryAnalyticsSortingQueryParamsTest().model_dump()

        response = await client.get(f"/api/repos/{owner}/{repo}/activity", params=dummy_query_params)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(
            [
                repo_analytics
                for repo_analytics in repos_analytics
                if repository["position_cur"] == repo_analytics["position"]
                and dummy_query_params["since"] <= repo_analytics["date"] <= dummy_query_params["until"]
            ]
        )

    async def test_repository_doesnt_exist(self, client, test_session):
        await RepositoryFactory(test_session).create_batch(100)
        owner, repo = fake.name(), fake.name()

        await RepositoryAnalyticsFactory(test_session).create_batch(1000)
        dummy_query_params = RepositoryAnalyticsSortingQueryParamsTest().model_dump()

        response = await client.get(f"/api/repos/{owner}/{repo}/activity", params=dummy_query_params)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == ErrorCodes.REPOSITORY_NOT_FOUND
