from fastapi import FastAPI, Depends, HTTPException, Path, APIRouter
from typing import Annotated

from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status

from ..models import Todos, User
from ..database import SessionLocal
from .auth import get_current_user

router = APIRouter(
    prefix='/user',
    tags=['User']
)

class UpdateUserPasswordRequest(BaseModel):
    old_password: str
    new_password: str


class UpdateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str

class UpdateUserPhoneNumberRequest(BaseModel):
    phone_number: str



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency =Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') ##Hashing variable


@router.get('/', status_code=status.HTTP_200_OK)
async def get_user_details(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication credentials were not provided')

    current_user = db.query(User).filter(User.id == user.get('user_id')).first()
    return current_user


@router.put('/updatepassword', status_code=status.HTTP_202_ACCEPTED)
async def update_password(user: user_dependency, db: db_dependency, update_user_password_request: UpdateUserPasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication credentials were not provided')
    current_user_model = db.query(User).filter(User.id == user.get('user_id')).first()

    if not bcrypt_context.verify(update_user_password_request.old_password, current_user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Old password is incorrect')

    current_user_model.hashed_password = bcrypt_context.hash(update_user_password_request.new_password)
    db.add(current_user_model)
    db.commit()


@router.put('/updateuser', status_code=status.HTTP_202_ACCEPTED)
async def update_user(user: user_dependency, db: db_dependency, update_user_request: UpdateUserRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication credentials were not provided')
    current_user_model = db.query(User).filter(User.id == user.get('user_id')).first()

    current_user_model.first_name = update_user_request.first_name
    current_user_model.last_name = update_user_request.last_name
    current_user_model.email = update_user_request.email
    current_user_model.username = update_user_request.username

    db.add(current_user_model)
    db.commit()


@router.put('/updateuser/phonenumber', status_code=status.HTTP_202_ACCEPTED)
async def update_user_phone_number(user: user_dependency, db: db_dependency, update_user_phone_number_request: UpdateUserPhoneNumberRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail='Authentication credentials were not provided')
    current_user_model = db.query(User).filter(User.id == user.get('user_id')).first()

    current_user_model.phone_number = update_user_phone_number_request.phone_number

    db.add(current_user_model)
    db.commit()