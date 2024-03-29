import asyncio
import http

from aiohttp import ClientSession

from db import async_session_maker
from services import CommitDatabaseService, CommitsFetchService, RepositoriesDatabaseService, RepositoriesFetchService
from services.parser import GithubAPIRepositoriesParser, GithubAPICommitsAnalyticsParser
from settings import GITHUB_TOKEN


async def handler(event, context):
    async with (async_session_maker() as db_session, db_session.begin(), ClientSession() as http_session):
        repos_fetch_service = RepositoriesFetchService()
        repos_database_service = RepositoriesDatabaseService(db_session)
        github_repositories_parser = GithubAPIRepositoriesParser(
            fetch_service=repos_fetch_service, database_service=repos_database_service, token=GITHUB_TOKEN
        )
        repositories = await github_repositories_parser.parse(http_session)

        commits_fetch_service = CommitsFetchService()
        commits_database_service = CommitDatabaseService(db_session)
        github_commits_parser = GithubAPICommitsAnalyticsParser(
            fetch_service=commits_fetch_service,
            database_service=commits_database_service,
            repositories=repositories,
            token=GITHUB_TOKEN,
        )
        await github_commits_parser.parse(http_session)

        return {"statusCode": http.HTTPStatus.OK}


async def main():
    async with (async_session_maker() as db_session, db_session.begin(), ClientSession() as http_session):
        repos_fetch_service = RepositoriesFetchService()
        repos_database_service = RepositoriesDatabaseService(db_session)
        github_repositories_parser = GithubAPIRepositoriesParser(
            fetch_service=repos_fetch_service, database_service=repos_database_service, token=GITHUB_TOKEN
        )
        repositories = await github_repositories_parser.parse(http_session)

        commits_fetch_service = CommitsFetchService()
        commits_database_service = CommitDatabaseService(db_session)
        github_commits_parser = GithubAPICommitsAnalyticsParser(
            fetch_service=commits_fetch_service,
            database_service=commits_database_service,
            repositories=repositories,
            token=GITHUB_TOKEN,
        )
        await github_commits_parser.parse(http_session)


if __name__ == "__main__":
    asyncio.run(main())
