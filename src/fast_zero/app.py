from http import HTTPStatus

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.fast_zero.database import get_session
from src.fast_zero.models import User
from src.fast_zero.schemas import (
    MessageSchema,
    UserListSchema,
    UserPublicSchema,
    UserSchema,
)

app = FastAPI()


@app.get('/users', response_model=UserListSchema)
def get_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = session.scalars(select(User).offset(skip).limit(limit)).all()
    return {'users': users}


@app.get('/users/{user_id}', response_model=UserPublicSchema)
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserPublicSchema)
def create_user(user: UserSchema, session: Session = Depends(get_session)):
    query = select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )
    user_model = session.scalar(query)
    if user_model and user.username == user_model.username:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Username already exists'
        )
    elif user_model and user.email == user_model.email:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail='Email already exists'
        )
    user_model = User(
        username=user.username,
        password=user.password,
        email=user.email,
    )
    session.add(user_model)
    session.commit()
    session.refresh(user_model)
    return user_model


@app.put('/users/{user_id}', response_model=UserPublicSchema)
def update_user(
    user_id: int, user: UserSchema, session: Session = Depends(get_session)
):
    user_model = session.get(User, user_id)
    if user_model:
        try:
            user_model.username = user.username
            user_model.password = user.password
            user_model.email = user.email
            session.commit()
            session.refresh(user_model)
        except IntegrityError:
            raise HTTPException(
                status_code=HTTPStatus.CONFLICT,
                detail='Username or Email already exists',
            )
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    return user_model


@app.delete('/users/{user_id}', response_model=MessageSchema)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return {'message': 'User deleted'}
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@app.get('/', response_model=MessageSchema)
def read_root():
    return {'message': 'Hello World'}


@app.get('/html', response_class=HTMLResponse)
def read_root_html():
    return '<h1>Hello World</h1>'
