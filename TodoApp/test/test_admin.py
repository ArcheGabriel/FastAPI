from .utils import *
from ..routers.admin import get_db,get_current_user
from ..models import Todos

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_admin_read_all_authenticated(test_todo):
    response = client.get("/admin/todo")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{'complete':False,
                                'title':'Learn to Code',
                                'description':'Learn Code',
                                'priority':2,
                                'owner_id':1,
                                'id':1},]


def test_admin_delete_todo_authenticated(test_todo):
    response = client.delete('/admin/todo/deletetodo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None


def test_admin_delete_todo_not_found_authenticated(test_todo):
    response = client.delete('/admin/todo/deletetodo/5')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
