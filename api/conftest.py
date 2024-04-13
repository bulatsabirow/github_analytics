import asyncio
from contextlib import contextmanager
from typing import Callable

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from app.repo import RepositoryDatabaseService, RepositoryAnalyticsDatabaseService
from main import app
from services.db import get_async_session


@pytest.fixture(scope="session")
def test_db():
    db = PostgresContainer(image="postgres:14-alpine", driver="asyncpg")
    with db:
        yield db


@pytest.fixture(scope="session")
def test_engine(test_db):
    return create_async_engine(test_db.get_connection_url(), echo=True)


@pytest.fixture(scope="session")
def test_session_maker(test_engine):
    return async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=test_engine)


# test_engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=True)
# test_session_maker = async_sessionmaker(expire_on_commit=False, autocommit=False, autoflush=False, bind=test_engine)


@contextmanager
def dependencies_overrider(app: FastAPI, dependencies: dict[Callable, Callable]):
    app.dependency_overrides.update(dependencies)
    yield app
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


async def create_tables(session: AsyncSession):
    await RepositoryDatabaseService(session).create_table()
    await RepositoryAnalyticsDatabaseService(session).create_table()


async def drop_tables(session: AsyncSession):
    await RepositoryAnalyticsDatabaseService(session).drop_table(is_cascade=False)
    await RepositoryDatabaseService(session).drop_table(is_cascade=True)


@pytest.fixture
async def test_session(test_session_maker):
    async with test_session_maker() as test_session:
        # __enter__ - create test tables and open new database session
        await create_tables(test_session)
        await test_session.commit()
        yield test_session

        # __exit__ - drop test tables and close session
        await drop_tables(test_session)
        await test_session.commit()


@pytest.fixture
async def client(test_session):
    overridden_dependencies = {get_async_session: lambda: test_session}

    with dependencies_overrider(app, overridden_dependencies) as test_app:
        async with AsyncClient(
            app=test_app,
            base_url="http://test",
        ) as client:
            yield client
