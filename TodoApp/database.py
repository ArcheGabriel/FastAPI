from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


##For SQLite3
##SQLALCHEMY_DATABASE_URI = 'sqlite:///./todosapp.db'
#engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False})

##For PostgreSQL
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:root@localhost/TodoApplicationDatabase'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

##For Mysql
##SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:root@127.0.0.1:3306/todoapplicationdatabase'
##engine = create_engine(SQLALCHEMY_DATABASE_URL)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

