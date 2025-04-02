from http import HTTPStatus

from jwt import decode

from fast_zero.security import create_access_token, settings


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)
    decoded = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_jwt_invalid_token(client, user):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': 'Bearer token-invalido'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_without_email(client, user):
    invalid_token = create_access_token({})
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {invalid_token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_with_invalid_email(client, user):
    invalid_token = create_access_token({'sub': 'inexistente@gmail.com'})
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {invalid_token}'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
