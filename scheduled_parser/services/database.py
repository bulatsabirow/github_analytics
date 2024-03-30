import datetime
import functools
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def clean_data(func):
    """
    Cleans raw data and checks their presence.
    If there's no any data, just returns None.
    :param func: asynchronous function taking 1 parameter: raw_data
    :return: decorated function 'wrapper' having modified behavior
    """

    @functools.wraps(func)
    async def wrapper(self: BaseDatabaseService, raw_data):
        data = self.clean_raw_data(raw_data)
        if not data:
            return
        return await func(self, data)

    return wrapper


class BaseDatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert(self, raw_data: list[dict[str, Any]]):
        return NotImplemented

    def clean_item(self, item, pos):
        return NotImplemented

    def clean_raw_data(self, raw_data):
        return NotImplemented


class RepositoriesDatabaseService(BaseDatabaseService):
    def clean_item(self, item, pos):
        return {
            "full_name": item["full_name"],
            "owner": item["owner"]["login"],
            "position_cur": pos,
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
    async def bulk_insert(self, data: list[dict[str, Any]]):
        """
        Inserts data into the table 'repositories' as follows:
        1. Fetches already stored data and tries to find repositories which presented in fetched and stored data to
        fill in its field 'position_prev'.
        2. Upserts handled data into the table 'repositories'.
        :param data: list of dictionaries the keys of which match to database table 'repo_analytics'.
        """
        previous_data = (await self.session.execute(text("SELECT * FROM repositories;"))).mappings().all()
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
    def clean_item(self, item, pos):
        author = item["commit"]["author"]

        return dict(author=author["name"], date=datetime.datetime.fromisoformat(author["date"]).date(), position=pos)

    def clean_raw_data(self, raw_data):
        data = []
        for pos, repository_commits in enumerate(raw_data, start=1):
            # condition 'isinstance(item, dict)' checks whether valid response was retrieved or GitHub API requests
            # limit was exceeded
            data.extend([self.clean_item(item, pos) for item in repository_commits if isinstance(item, dict)])

        return data

    async def truncate_table(self):
        await self.session.execute(text("TRUNCATE TABLE repo_analytics;"))

    @clean_data
    async def bulk_insert(self, data: list[dict[str, Any]]):
        """
        Inserts data into the table 'repo_analytics' as follows:
        1. Creates temporary table 'temp_commits' in which fetched from API data will be temporarily stored.
        2. Inserts data into this table.
        3. Inserts data into major table using aggregated query.
        4. Truncates temporary table.
        :param data: list of dictionaries the keys of which match to database table 'repo_analytics'.
        """
        await self.session.execute(
            text(
                # temporary table exists for the duration of a database session
                """
                    CREATE TEMPORARY TABLE IF NOT EXISTS temp_commits(
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
        await self.session.execute(
            text(
                """
                    INSERT INTO public.repo_analytics(date, commits, authors, position) SELECT date, count(date) as commmits,
                    array_agg(distinct author) as authors, position from temp_commits group by date, position
                     ON CONFLICT(date, position) DO UPDATE SET commits = public.repo_analytics.commits + excluded.commits,
                     authors = (select array_agg(distinct alias.item) from
                     -- select distinct authors from array
                     (select unnest(public.repo_analytics.authors || excluded.authors) as item) alias
                      where item is not null);
                """
            )
        )
        await self.session.execute(text("TRUNCATE TABLE temp_commits;"))
