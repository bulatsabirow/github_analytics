import asyncio
import http

from aiohttp import ClientSession

from db import get_async_session_maker
from services import CommitDatabaseService, CommitsFetchService, RepositoriesDatabaseService, RepositoriesFetchService
from services.parser import GithubAPIRepositoriesParser, GithubAPICommitsAnalyticsParser
from settings import GITHUB_TOKEN, DB_USER, DB_HOST, DB_PORT, DB_NAME

# maximum pages count for each repository which will be parsed
UNAUTHENTICATED_PAGINATION_LIMIT = 2
# value '41' was chosen to ensure that GitHub won't block account
AUTHENTICATED_PAGINATION_LIMIT = 41


async def handler(event, context):
    auth_headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    DB_PASSWORD = context.token.get("access_token")
    DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    async_session_maker = get_async_session_maker(DATABASE_URL)
    async with (ClientSession(headers=auth_headers) as http_session):
        async with async_session_maker() as db_session, db_session.begin():
            repos_fetch_service = RepositoriesFetchService()
            repos_database_service = RepositoriesDatabaseService(db_session)
            github_repositories_parser = GithubAPIRepositoriesParser(
                fetch_service=repos_fetch_service, database_service=repos_database_service, token=GITHUB_TOKEN
            )
            repositories = await github_repositories_parser.parse(http_session)
            commits_database_service = CommitDatabaseService(db_session)
            # truncate table 'repo_analytics' as data stored in it already irrelevant
            await commits_database_service.truncate_table()

        for page in range(1, AUTHENTICATED_PAGINATION_LIMIT if auth_headers else UNAUTHENTICATED_PAGINATION_LIMIT):
            # retrieve data from GitHub API about commit statistics and
            # load it into database on each iteration
            async with async_session_maker() as db_session, db_session.begin():
                commits_fetch_service = CommitsFetchService()
                commits_database_service = CommitDatabaseService(db_session)
                github_commits_parser = GithubAPICommitsAnalyticsParser(
                    fetch_service=commits_fetch_service,
                    database_service=commits_database_service,
                    repositories=repositories,
                    token=GITHUB_TOKEN,
                )
                await github_commits_parser.parse(http_session, page=page)

        return {"statusCode": http.HTTPStatus.OK}
