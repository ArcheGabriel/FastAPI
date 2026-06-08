from urllib import response

from httpcore import request
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from starlette import status


from ..database import Base
from ..main import app

from fastapi.testclient import TestClient
from fastapi import status

import pytest
from ..models import Todos, User
from ..routers.auth import bcrypt_context



SQLALCHEMY_DATABASE_URI = 'sqlite:///./testdb.db'

engine = create_engine(SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False},poolclass=StaticPool)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username':'ArcheGabriel','user_id':1,'user_role':'Admin'}



client = TestClient(app)



@pytest.fixture
def test_todo():
    todo = Todos(
        title='Learn to Code',
        description='Learn Code',
        priority=2,
        complete=False,
        owner_id=1,
    )

    db =TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

@pytest.fixture
def test_user():
    user = User(
        username='Arche_Gabriel',
        id=1,
        role='Admin',
        email='rupkumar2804@gmail.com',
        first_name='Arche',
        last_name='Gabriel',
        hashed_password=bcrypt_context.hash('testpassword'),
        phone_number='+917003919912'
    )

    db =TestingSessionLocal()
    db.add(user)
    db.commit()
    yield user
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM users;"))
        connection.commit()