import re
from datetime import timedelta, datetime, timezone
from typing import Annotated

import phonenumbers
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr, field_validator, Field
from sqlalchemy.orm import Session
from starlette import status

from ..database import SessionLocal
from ..models import User
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = '512bdc1f149986d7859068d66d7a7406bac3adae24563567abcf41cb9e0b138b'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') ##Hashing variable

oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    password: str
    phone_number: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value):
        try:
            parsed = phonenumbers.parse(value, None)

            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone number")

            return value

        except Exception:
            raise ValueError("Invalid phone number")


    @field_validator("password")
    @classmethod
    def check_password_strength(cls,value):
        if len(value) < 8:
            raise ValueError(
                "Password must be at least 8 characters long"
            )

        if not re.search(r"[A-Z]", value):
            raise ValueError(
                "Password must contain at least one uppercase letter"
            )

        if not re.search(r"[a-z]", value):
            raise ValueError(
                "Password must contain at least one lowercase letter"
            )

        if not re.search(r"\d", value):
            raise ValueError(
                "Password must contain at least one digit"
            )

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?]", value):
            raise ValueError(
                "Password must contain at least one special character"
            )

        return value



class Token(BaseModel):
    access_token: str
    token_type: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency =Annotated[Session, Depends(get_db)]

templates = Jinja2Templates(directory='TodoApp/templates')

### Pages ###

@router.get("/login-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@router.get("/register-page")
def render_login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )

### Enpoints ###
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires =  datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
        return {'username': username, 'user_id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):

    existing_email = db.query(User).filter(User.email == create_user_request.email).first()
    existing_phone_number = db.query(User).filter(User.phone_number == create_user_request.phone_number).first()
    existing_username = db.query(User).filter(User.username == create_user_request.username).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already registered')
    elif existing_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Username already registered')
    elif existing_phone_number:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Phone number already registered')
    else:
        create_user_model = User(
            username=create_user_request.username,
            email=create_user_request.email,
            first_name=create_user_request.first_name,
            last_name=create_user_request.last_name,
            hashed_password=bcrypt_context.hash(create_user_request.password),
            role="User",
            is_active=True,
            phone_number=create_user_request.phone_number
        )

        db.add(create_user_model)
        db.commit()


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate credentials')
    token = create_access_token(user.username, user.id,user.role ,timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}
