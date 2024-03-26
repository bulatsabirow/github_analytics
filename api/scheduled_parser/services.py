import asyncio
from typing import Generator, Any

from aiohttp import ClientSession
from sqlalchemy import exc, text
from sqlalchemy.ext.asyncio import AsyncSession

from scheduled_parser.db import get_async_session

urls = [
    "https://api.github.com/search/repositories?q=stars%3A%3E0&sort=stars&order=desc&page=1&per_page=100",
]


async def bulk_insert(session: AsyncSession, data: list[dict[str, Any]]):
    try:
        previous_data = (await session.execute(text("SELECT * FROM repositories order by repo;"))).mappings().all()
        for item in data:
            for prev_item in previous_data:
                if item["full_name"] == prev_item["repo"]:
                    item["position_prev"] = prev_item["position_cur"]
                    break

        await session.execute(
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
                language = excluded.language
                ;
            """
            ),
            data,
        )
    except exc.SQLAlchemyError as e:
        await session.rollback()
    else:
        await session.commit()


def clean_json(item: dict[str, Any], pos) -> dict[str, Any]:
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


def clean_raw_data(raw_data: list[dict]) -> list[dict]:
    return [clean_json(item, pos) for pos, item in enumerate(raw_data, start=1)]


async def fetch_resource(url: str, session: ClientSession):
    async with session.get(url) as response:
        response_data = await response.json()
        return response_data.get("items", [])


async def fetch_resources(urls: list[str]):
    tasks = []
    async with ClientSession() as session:
        for url in urls:
            tasks.append(fetch_resource(url, session))

        return await asyncio.gather(*tasks)


async def main():
    session = await anext(get_async_session())
    results = map(clean_raw_data, await fetch_resources(urls))
    await asyncio.gather(*[bulk_insert(session, result) for result in results])


if __name__ == "__main__":
    asyncio.run(main())
