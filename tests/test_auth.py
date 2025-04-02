from http import HTTPStatus


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': user.cleaned_password},
    )
    token = response.json()
    assert response.status_code == HTTPStatus.OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_incorrect_email(client, user):
    response = client.post(
        '/auth/token',
        data={'username': 'invalido@gmail.com', 'password': user.cleaned_password},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_incorrect_password(client, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': '12345'},
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}
