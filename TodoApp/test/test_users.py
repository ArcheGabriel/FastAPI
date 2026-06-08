from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

def test_return_user(test_user):
    response = client.get("/user/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == 'Arche_Gabriel'
    assert response.json()['first_name'] == 'Arche'
    assert response.json()['last_name'] == 'Gabriel'
    assert response.json()['email'] == 'rupkumar2804@gmail.com'
    assert response.json()['phone_number'] == '+917003919912'
    assert response.json()['role'] == 'Admin'



def test_change_password_success(test_user):
    response = client.put("/user/updatepassword", json={'old_password': 'testpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_202_ACCEPTED

def test_change_password_invalid_current_password(test_user):
    response = client.put("/user/updatepassword", json={'old_password': 'wrongpassword', 'new_password': 'newpassword'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Old password is incorrect'}


def test_change_phone_number_success(test_user):
    response = client.put("/user/updateuser/phonenumber", json={'phone_number': '+919088556113'})
    assert response.status_code == status.HTTP_202_ACCEPTED


def test_update_user_details(test_user):
    request_data = {
        'username': 'Arche_Gabriel',
        'first_name': 'Arche',
        'last_name': 'Gabriel',
        'email': 'changedemail@gmail.com',
    }
    response = client.put("/user/updateuser", json=request_data)
    assert response.status_code == status.HTTP_202_ACCEPTED

