from urllib import response

from httpcore import request
from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from starlette import status

from ..routers.todos import get_db, get_current_user
from ..database import Base
from ..main import app

from fastapi.testclient import TestClient
from fastapi import status

import pytest
from ..models import Todos

from .utils import *



app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)


def test_read_all_authenticated(test_todo):
    response = client.get("/todos/alltodos")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete':False,
                                'title':'Learn to Code',
                                'description':'Learn Code',
                                'priority':2,
                                'owner_id':1,
                                'id':1},]


def test_read_one_authenticated(test_todo):
    response = client.get("/todos/todo/get_todo_by_id/1")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'complete':False,
                                'title':'Learn to Code',
                                'description':'Learn Code',
                                'priority':2,
                                'owner_id':1,
                                'id':1}

def test_read_one_authenticated_not_found():
    response = client.get("/todos/todo/get_todo_by_id/5")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}



def test_create_todo(test_todo):
    request_data={
        'title':'New Todo',
        'description':'New todo description',
        'priority':2,
        'complete':False,
    }

    response = client.post("/todos/todo/addtodo", json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    model= db.query(Todos).filter(Todos.id==2).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')



def test_update_todo(test_todo):
    request_data={
        'title': 'Change the title of the todo already saved',
        'description':'Learn Code',
        'priority':2,
        'complete':False,
    }

    response = client.put('/todos/todo/updatetodo/1', json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data.get('title')
    assert model.description == request_data.get('description')
    assert model.priority == request_data.get('priority')
    assert model.complete == request_data.get('complete')


def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'Change the title of the todo already saved',
        'description': 'Learn Code',
        'priority': 2,
        'complete': False,
    }

    response = client.put('/todos/todo/updatetodo/5', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}



def test_delete_todo(test_todo):
    response = client.delete('/todos/todo/deletetodo/1')
    assert response.status_code == status.HTTP_202_ACCEPTED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id==1).first()
    assert model is None


def test_delete_todo_not_found(test_todo):
    response = client.delete("/todos/todo/deletetodo/5")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}