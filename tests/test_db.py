from dataclasses import asdict

import pytest
from sqlalchemy import select

from fast_zero.models import Task, User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    with mock_db_time(model=User) as time:
        new_user = User(username='alice', password='secret', email='teste@test')
        session.add(new_user)
        await session.commit()
        user = await session.scalar(select(User).where(User.username == 'alice'))
        assert asdict(user) == {
            'id': 1,
            'username': 'alice',
            'password': 'secret',
            'email': 'teste@test',
            'tasks': [],
            'created_at': time,
            'updated_at': time,
        }


@pytest.mark.asyncio
async def test_create_task(session, user):
    task = Task(
        title='Test Task',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )
    session.add(task)
    await session.commit()
    task = await session.scalar(select(Task))
    assert asdict(task) == {
        'description': 'Test Desc',
        'id': 1,
        'state': 'draft',
        'title': 'Test Task',
        'user_id': 1,
    }


@pytest.mark.asyncio
async def test_user_task_relationship(session, user):
    task = Task(
        title='Test Task',
        description='Test Desc',
        state='draft',
        user_id=user.id,
    )
    session.add(task)
    await session.commit()
    await session.refresh(user)
    user = await session.scalar(select(User).where(User.id == user.id))
    assert user.tasks == [task]
