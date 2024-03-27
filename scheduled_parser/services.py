import asyncio
import functools
from typing import Generator, Any, Callable, Optional

from aiohttp import ClientSession
from sqlalchemy import exc, text
from sqlalchemy.ext.asyncio import AsyncSession

from scheduled_parser.db import async_session_maker

repositores_url = "https://api.github.com/search/repositories?q=stars%3A%3E0&sort=stars&order=desc&page=1&per_page=100"
base_commits_url = "https://api.github.com/repos/%s/commits"


class BaseFetchService:
    base_url: Optional[str] = None

    async def fetch_resource(self, session: ClientSession, url: str):
        async with session.get(url) as response:
            response_data = await response.json()
            return response_data

    async def fetch_resources(self, urls: list[str]):
        print(urls)
        tasks = []
        async with ClientSession() as session:
            for url in urls:
                tasks.append(self.fetch_resource(session, url))

            return await asyncio.gather(*tasks)


class RepositoriesFetchService(BaseFetchService):
    base_url = repositores_url

    async def fetch_resource(self, session: ClientSession, url: str):
        return (await super().fetch_resource(session, url)).get("items", [])

    async def fetch_repositories(self):
        async with ClientSession() as session:
            task = asyncio.create_task(self.fetch_resource(session, self.base_url))
            await task
            return task.result()


class CommitsFetchService(BaseFetchService):
    lock = asyncio.Lock()

    base_url = base_commits_url

    async def fetch_resource(self, session: ClientSession, url: str):
        async with self.lock:
            await asyncio.sleep(10)
            async with session.get(url) as response:
                response_data = await response.json()
                print(f"{response_data}")
                return response_data


class BaseDatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert(self, data: list[dict[str, Any]]):
        return NotImplemented

    def clean_item(self, item, **kwargs):
        return NotImplemented

    def clean_raw_data(self, raw_data):
        return NotImplemented


class RepositoriesDatabaseService(BaseDatabaseService):
    def clean_item(self, item, **kwargs):
        return {
            # TODO set 'pos' as func argument
            "full_name": item["full_name"],
            "owner": item["owner"]["login"],
            "position_cur": kwargs["pos"],
            "position_prev": item.get("position_prev"),
            "stars": item["stargazers_count"],
            "watchers": item["watchers"],
            "forks": item["forks"],
            "open_issues": item["open_issues_count"],
            "language": item["language"],
        }

    def clean_raw_data(self, raw_data):
        return [self.clean_item(item, pos=pos) for pos, item in enumerate(raw_data, start=1)]

    async def bulk_insert(self, raw_data, is_atomic=True):
        data = self.clean_raw_data(raw_data)
        previous_data = (await self.session.execute(text("SELECT * FROM repositories order by repo;"))).mappings().all()
        for item in data:
            for prev_item in previous_data:
                if item["full_name"] == prev_item["repo"]:
                    item["position_prev"] = prev_item["position_cur"]
                    break
        await self.session.execute(
            text(
                """
                INSERT INTO repositories (
                    repo,
                    owner,
                    position_cur,
                    position_prev,
                    stars,
                    watchers,
                    forks,
                    open_issues,
                    language)
                    VALUES (
                    :full_name,
                    :owner,
                    :position_cur,
                    :position_prev,
                    :stars,
                    :watchers,
                    :forks,
                    :open_issues,
                    :language
                    ) 
                    ON CONFLICT (position_cur)
                    DO UPDATE SET repo = excluded.repo,
                    position_prev = excluded.position_prev,
                    owner = excluded.owner,
                    stars = excluded.stars,
                    watchers = excluded.watchers,
                    forks = excluded.forks,
                    open_issues = excluded.open_issues,
                    language = excluded.language;
                """
            ),
            data,
        )


class CommitDatabaseService(BaseDatabaseService):
    def clean_item(self, item, **kwargs):
        print(f"{item}")
        author = item["commit"]["author"]

        return dict(author=author["name"], date=author["date"], position=kwargs["pos"])

    def clean_raw_data(self, raw_data):
        data = []
        for pos, repository_commits in enumerate(raw_data, start=1):
            print(f"{repository_commits=}")
            data.extend([self.clean_item(item, pos=pos) for item in repository_commits])

        return data

    async def bulk_insert(self, raw_data: list[dict[str, Any]]):
        data = self.clean_raw_data(raw_data)
        await self.session.execute(
            text(
                """
                    CREATE TEMPORARY TABLE temp_commits(
                        author varchar(256),
                        date date,
                        position bigserial
                    )
                """
            )
        )
        await self.session.execute(
            text(
                """
                    INSERT INTO temp_commits(author, date, position) VALUES (
                        :author,
                        :date,
                        :position
                    )
                    """
            ),
            data,
        )
        await self.session.execute(text("TRUNCATE TABLE repo_analytics;"))
        await self.session.execute(
            text(
                """
                    INSERT INTO public.repo_analytics(date, commits, authors, position) SELECT date, count(date) as commmits,
                    array_agg(author) as authors, position from temp_commits group by date, position;
                    """
            )
        )


async def main():
    async with async_session_maker() as session, session.begin():
        repos_fetch_service = RepositoriesFetchService()
        repositories = await repos_fetch_service.fetch_repositories()
        repos_database_service = RepositoriesDatabaseService(session)
        await repos_database_service.bulk_insert(raw_data=repositories)

        # commits_fetch_service = CommitsFetchService()
        # repositories_commits = \
        #     await commits_fetch_service.fetch_resources([base_commits_url % repo.get("full_name")
        #                                                  for repo in repositories][:5])
        # commits_database_service = CommitDatabaseService(session)


if __name__ == "__main__":
    asyncio.run(main())
