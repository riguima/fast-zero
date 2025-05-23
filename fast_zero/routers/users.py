from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import User
from fast_zero.security import get_current_user, get_password_hash

router = APIRouter(prefix='/users', tags=['users'])

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
T_FilterPage = Annotated[schemas.FilterPage, Query()]


@router.get('/', response_model=schemas.UserList)
async def get_users(filter_page: T_FilterPage, session: T_Session):
    query = await session.scalars(
        select(User).offset(filter_page.offset).limit(filter_page.limit)
    )
    users = query.all()
    return {'users': users}


@router.get('/{user_id}', response_model=schemas.UserPublic)
async def get_user(user_id: int, session: T_Session):
    user = await session.get(User, user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')


@router.post('/', status_code=HTTPStatus.CREATED, response_model=schemas.UserPublic)
async def create_user(user: schemas.User, session: T_Session):
    query = select(User).where(
        (User.username == user.username) | (User.email == user.email)
    )
    user_model = await session.scalar(query)
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
        password=get_password_hash(user.password),
        email=user.email,
    )
    session.add(user_model)
    await session.commit()
    await session.refresh(user_model)
    return user_model


@router.put('/{user_id}', response_model=schemas.UserPublic)
async def update_user(
    user_id: int,
    user: schemas.User,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    try:
        current_user.username = user.username
        current_user.password = get_password_hash(user.password)
        current_user.email = user.email
        await session.commit()
        await session.refresh(current_user)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail='Username or Email already exists',
        )
    return current_user


@router.delete('/{user_id}', response_model=schemas.Message)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail='Not enough permissions'
        )
    await session.delete(current_user)
    await session.commit()
    return {'message': 'User deleted'}
