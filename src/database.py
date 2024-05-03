from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_async_engine(DATABASE_URL)

new_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Базовый класс для моделей
class Model(DeclarativeBase):
      pass

# Модель таблицы users
class UsersOrm(Model):
      __tablename__ = 'users'

      id = Column(UUID(as_uuid=True), primary_key=True)
      created_at = Column(String, nullable=False)
      login = Column(String, unique=True, nullable=False)
      password = Column(String, unique=True, nullable=False)
      project_id = Column(UUID(as_uuid=True), nullable=False)
      env = Column(String)
      domain = Column(String)
      locktime = Column(String, nullable=True)

# Создание таблиц
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)