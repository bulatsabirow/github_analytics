import pprint
from typing import Optional, ClassVar
from urllib.parse import urlencode

from aiohttp import ClientSession

from services import BaseDatabaseService, BaseFetchService


class GithubAPIParser:
    """
    Base class for parsing GitHub API endpoints
    """

    def __init__(
        self, fetch_service: BaseFetchService, database_service: BaseDatabaseService, token: Optional[str] = None
    ):
        self.token = token
        self.database_service = database_service
        self.fetch_service = fetch_service

    @property
    def is_authenticated(self):
        return self.token is not None and self.token != ""

    async def parse(self, http_session: ClientSession):
        return NotImplemented


class GithubAPIRepositoriesParser(GithubAPIParser):
    async def parse(self, http_session: ClientSession) -> list:
        repositories = await self.fetch_service.fetch_resource(http_session)
        await self.database_service.bulk_insert(raw_data=repositories)
        return repositories


class GithubAPICommitsAnalyticsParser(GithubAPIParser):
    def __init__(
        self,
        fetch_service: BaseFetchService,
        database_service: BaseDatabaseService,
        repositories: list,
        token: Optional[str] = None,
    ):
        super().__init__(fetch_service=fetch_service, database_service=database_service, token=token)
        self.repositories = repositories

    async def parse(self, http_session: ClientSession) -> None:
        repositories_commits = []

        for page in range(1, 2 if self.is_authenticated else 2):
            urls = [
                self.fetch_service.base_url % (repo.get("full_name"), urlencode({"page": page, "per_page": 100}))
                for repo in self.repositories
            ]
            if not self.is_authenticated:
                # 60 - 1 = 59 requests left, 1 request was already done
                urls = urls[:59]

            repositories_commits.extend(await self.fetch_service.fetch_resources(urls, http_session))

        await self.database_service.bulk_insert(repositories_commits)
