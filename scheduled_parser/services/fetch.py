import asyncio
import os
from typing import ClassVar

from aiohttp import ClientSession

"""
Github API requests limit for authenticated users is 5000 requests per hour.
Github API requests limit for unauthenticated users is 60 requests per hour.
Yandex Serverless Cloud Function max timeout interval is 10 minutes, so need to produce maximum allowed requests count
for 10 minutes, delay between requests can be calculated as 600 seconds / 5000 = 0.12 seconds
 and 600 seconds / 60 = 10 seconds.
"""
DELAY = 0.12 if os.environ.get("GITHUB_TOKEN") else 10


class BaseFetchService:
    base_url: ClassVar[str] = ""

    async def fetch_resource(self, session: ClientSession, url: str):
        print("Fetching resource ", url)
        async with session.get(url) as response:
            response_data = await response.json()
            return response_data

    async def fetch_resources(self, urls: list[str], session: ClientSession):
        tasks = []
        for url in urls:
            tasks.append(self.fetch_resource(session, url))

        return await asyncio.gather(*tasks)


class RepositoriesFetchService(BaseFetchService):
    base_url = "https://api.github.com/search/repositories?q=stars%3A%3E0&sort=stars&order=desc&page=1&per_page=100"

    async def fetch_resource(self, session: ClientSession, url: str = ""):
        task = asyncio.create_task((super().fetch_resource(session, url or self.base_url)))
        await task
        return task.result().get("items", [])


class CommitsFetchService(BaseFetchService):
    base_url = "https://api.github.com/repos/%s/commits?%s"
    lock = asyncio.Lock()

    async def fetch_resource(self, session: ClientSession, url: str):
        async with self.lock:
            await asyncio.sleep(DELAY)
            return await super().fetch_resource(session, url)
