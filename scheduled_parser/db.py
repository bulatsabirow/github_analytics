from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from settings import DATABASE_URL

engine = create_async_engine(url=DATABASE_URL, echo=True)
async_session_maker = async_sessionmaker(engine, autoflush=False)
