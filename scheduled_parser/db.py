from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


def get_async_session_maker(database_url: str):
    engine = create_async_engine(url=database_url, echo=True, connect_args={"statement_cache_size": 0})
    async_session_maker = async_sessionmaker(engine, autoflush=False, expire_on_commit=False, autocommit=False)
    return async_session_maker
