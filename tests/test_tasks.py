from http import HTTPStatus

import factory
import factory.fuzzy
import pytest

from fast_zero.models import Task, TaskState


class TaskFactory(factory.Factory):
    class Meta:
        model = Task

    title = factory.Faker('text')
    description = factory.Faker('text')
    state = factory.fuzzy.FuzzyChoice(TaskState)
    user_id = 1


def test_create_task(client, token):
    response = client.post(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'title': 'Test Task',
            'description': 'Test Task Description',
            'state': 'draft',
        },
    )
    assert response.json() == {
        'id': 1,
        'title': 'Test Task',
        'description': 'Test Task Description',
        'state': 'draft',
    }


@pytest.mark.asyncio
async def test_list_tasks_should_return_5_tasks(session, client, user, token):
    expected_tasks = 5
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get(
        '/tasks/',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_pagination_should_return_2_tasks(
    session, user, client, token
):
    expected_tasks = 2
    session.add_all(TaskFactory.create_batch(5, user_id=user.id))
    await session.commit()
    response = client.get(
        '/tasks/',
        params={'offset': 1, 'limit': 2},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_filter_title_should_return_2_tasks(
    session, user, client, token
):
    expected_tasks = 2
    session.add_all(
        TaskFactory.create_batch(2, user_id=user.id, title='Test task 1'),
    )
    session.add_all(
        TaskFactory.create_batch(5, user_id=user.id, title='Another Title'),
    )
    await session.commit()
    response = client.get(
        '/tasks/',
        params={'title': 'test task'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_filter_description_should_return_3_tasks(
    session, user, client, token
):
    expected_tasks = 3
    session.add_all(
        TaskFactory.create_batch(3, user_id=user.id, description='My Description'),
    )
    session.add_all(
        TaskFactory.create_batch(5, user_id=user.id, description='Another Description'),
    )
    await session.commit()
    response = client.get(
        '/tasks/',
        params={'description': 'my des'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_filter_state_should_return_4_tasks(
    session, user, client, token
):
    expected_tasks = 4
    session.add_all(
        TaskFactory.create_batch(4, user_id=user.id, state='draft'),
    )
    session.add_all(
        TaskFactory.create_batch(1, user_id=user.id, state='todo'),
    )
    session.add_all(
        TaskFactory.create_batch(3, user_id=user.id, state='done'),
    )
    await session.commit()
    response = client.get(
        '/tasks/',
        params={'state': 'draft'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_list_tasks_filter_combined_should_return_5_tasks(
    session, user, client, token
):
    expected_tasks = 5
    session.add_all(
        TaskFactory.create_batch(
            5,
            user_id=user.id,
            title='my title',
            description='my description',
            state='done',
        ),
    )
    session.add_all(
        TaskFactory.create_batch(
            1,
            user_id=user.id,
            title='wrong',
            description='my description',
            state='draft',
        ),
    )
    session.add_all(
        TaskFactory.create_batch(
            2,
            user_id=user.id,
            title='wrong',
            description='wrong',
            state='done',
        ),
    )
    session.add_all(
        TaskFactory.create_batch(
            7,
            user_id=user.id,
            title='my title',
            description='wrong',
            state='doing',
        ),
    )
    await session.commit()
    response = client.get(
        '/tasks/',
        params={'state': 'done', 'description': 'desc', 'title': 'my t'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert len(response.json()['tasks']) == expected_tasks


@pytest.mark.asyncio
async def test_patch_task(session, client, user, token):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    await session.commit()
    response = client.patch(
        f'/tasks/{task.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_patch_task_error(client, token):
    response = client.patch(
        '/tasks/10',
        json={},
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


@pytest.mark.asyncio
async def test_delete_task(session, client, user, token):
    task = TaskFactory(user_id=user.id)
    session.add(task)
    await session.commit()
    response = client.delete(
        f'/tasks/{task.id}',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'message': 'Task has been deleted successfully.'}


def test_delete_task_error(client, token):
    response = client.delete(
        '/tasks/10',
        headers={'Authorization': f'Bearer {token}'},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
