import datetime
import functools
import pprint
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def clean_data(func):
    @functools.wraps(func)
    async def wrapper(self: BaseDatabaseService, raw_data):
        data = self.clean_raw_data(raw_data)
        if not data:
            await self.session.rollback()
        return await func(self, data)

    return wrapper


class BaseDatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert(self, raw_data: list[dict[str, Any]]):
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

    @clean_data
    async def bulk_insert(self, data):
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
        print(f"{item=}")
        author = item["commit"]["author"]

        return dict(
            author=author["name"], date=datetime.datetime.fromisoformat(author["date"]).date(), position=kwargs["pos"]
        )

    def clean_raw_data(self, raw_data):
        pprint.pprint(f"{raw_data=}")
        pprint.pprint(f"{len(raw_data)=}")
        data = []
        for pos, repository_commits in enumerate(raw_data, start=1):
            data.extend([self.clean_item(item, pos=pos) for item in repository_commits if isinstance(item, dict)])

        return data

    @clean_data
    async def bulk_insert(self, data: list[dict[str, Any]]):
        await self.session.execute(
            text(
                """
                    CREATE TEMPORARY TABLE temp_commits(
                        author varchar(256),
                        date date,
                        position integer
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
                    array_agg(distinct author) as authors, position from temp_commits group by date, position;
                    """
            )
        )
