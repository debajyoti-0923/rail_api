from sqlalchemy import create_engine
from sqlalchemy.orm  import sessionmaker,DeclarativeBase

SQL_DB_URL="sqlite:///./rail_api.db"

engine=create_engine(
    SQL_DB_URL,
    connect_args={
        "check_same_thread":False
    }
)

sessionlocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

class base(DeclarativeBase):
    pass
