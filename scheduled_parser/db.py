from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


def get_async_session_maker(database_url: str):
    engine = create_async_engine(url=database_url, echo=True)
    async_session_maker = async_sessionmaker(engine, autoflush=False)
    return async_session_maker
