from sqlalchemy import create_engine
from sqlalchemy.orm  import sessionmaker,DeclarativeBase

SQL_DB_URL="sqlite:///./rail_api.db"
# SQL_DB_URL="postgresql://postgres:root@localhost:5432/railapi"

engine=create_engine(
    SQL_DB_URL,
    pool_size=50,
    echo=False
)

sessionlocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class base(DeclarativeBase):
    pass
