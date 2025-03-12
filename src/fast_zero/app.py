from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_zero.schemas import (
    MessageSchema,
    UserDB,
    UserList,
    UserSchema,
)

app = FastAPI()


database = []


@app.get('/users', response_model=UserList)
def get_users():
    return {'users': database}


@app.get('/users/{user_id}', response_model=UserDB)
def get_user(user_id: int):
    try:
        return next(filter(lambda u: u.id == user_id, database))
    except StopIteration:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@app.post('/users', status_code=HTTPStatus.CREATED, response_model=UserDB)
def create_user(user: UserSchema):
    user_with_id = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(user_with_id)
    return user_with_id


@app.put('/users/{user_id}', response_model=UserDB)
def update_user(user_id: int, user: UserSchema):
    try:
        user_found = next(filter(lambda u: u.id == user_id, database))
    except StopIteration:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[database.index(user_found)] = user_with_id
    return user_with_id


@app.delete('/users/{user_id}', response_model=MessageSchema)
def delete_user(user_id: int):
    try:
        user = next(filter(lambda u: u.id == user_id, database))
    except StopIteration:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    del database[database.index(user)]
    return {'message': 'User deleted'}


@app.get('/', response_model=MessageSchema)
def read_root():
    return {'message': 'Hello World'}


@app.get('/html', response_class=HTMLResponse)
def read_root_html():
    return '<h1>Hello World</h1>'
