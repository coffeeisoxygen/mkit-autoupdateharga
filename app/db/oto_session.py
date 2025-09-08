"""session for database


pada project ini menggunakan SQLAlchemy sebagai ORM (Object Relational Mapper) untuk berinteraksi dengan database.
session akan ada 2 :
1. app_session : koneksi ke database aplikasi, (sqlite) dengan aiosqlite
2. oto_session : koneksi ke otomax , (sqlserver) dengan pyodbc dan encrypted constring
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

sqlserver_engine = create_async_engine(
    url="mssql+aioodbc://user:password@host/dbname?driver=ODBC+Driver+17+for+SQL+Server",
    echo=True,
)
SqlserverAsyncSessionLocal = async_sessionmaker(
    bind=sqlserver_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
