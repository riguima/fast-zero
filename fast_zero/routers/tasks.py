from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fast_zero import schemas
from fast_zero.database import get_session
from fast_zero.models import Task, User
from fast_zero.security import get_current_user

router = APIRouter(prefix='/tasks', tags=['tasks'])


T_Session = Annotated[AsyncSession, Depends(get_session)]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=schemas.TaskPublic)
async def create_task(
    task: schemas.Task,
    current_user: T_CurrentUser,
    session: T_Session,
):
    task_model = Task(
        title=task.title,
        description=task.description,
        state=task.state,
        user_id=current_user.id,
    )
    session.add(task_model)
    await session.commit()
    await session.refresh(task_model)
    return task_model


@router.get('/', response_model=schemas.TaskList)
async def get_tasks(
    filter_task: Annotated[schemas.FilterTask, Query()],
    current_user: T_CurrentUser,
    session: T_Session,
):
    query = select(Task).where(Task.user_id == current_user.id)
    if filter_task.title:
        query = query.where(Task.title.icontains(filter_task.title))
    if filter_task.description:
        query = query.where(Task.description.icontains(filter_task.description))
    if filter_task.state:
        query = query.where(Task.state == filter_task.state)
    tasks = await session.scalars(
        query.offset(filter_task.offset).limit(filter_task.limit)
    )
    return {'tasks': tasks.all()}


@router.patch('/{task_id}', response_model=schemas.TaskPublic)
async def update_task(
    task_id: int,
    current_user: T_CurrentUser,
    session: T_Session,
    task: schemas.TaskUpdate,
):
    task_model = await session.scalar(
        select(Task).where(Task.user_id == current_user.id, Task.id == task_id)
    )
    if task_model is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Task not found.')
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(task_model, key, value)
    session.add(task_model)
    await session.commit()
    await session.refresh(task_model)
    return task_model


@router.delete('/{task_id}', response_model=schemas.Message)
async def delete_task(task_id: int, session: T_Session, current_user: T_CurrentUser):
    task = await session.scalar(
        select(Task).where(Task.user_id == current_user.id, Task.id == task_id)
    )
    if task is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Task not found.',
        )
    await session.delete(task)
    await session.commit()
    return {'message': 'Task has been deleted successfully.'}
