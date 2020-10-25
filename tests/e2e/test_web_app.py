import pytest

from flask import session

from movies.authentication.services import AuthenticationException
from movies.movie_library import services as movie_library_services
from movies.authentication import services as auth_services
from movies.movie_library.services import NonExistentMovieException
from movies.domain.model1 import Movie, Genre, Director, Actor, Review, User

def test_register(client):
    response_code = client.get('/authentication/register').status_code
    assert response_code == 200

    response = client.post(
        '/authentication/register',
        data={'username': 'hameshP', 'password': 'HameshPatel123'}
    )

    assert response.headers['Location'] == 'http://localhost/authentication/login'


@pytest.mark.parametrize(('username', 'password', 'message'), (
        ('', '', b'Your username is required'),
        ('cj', '', b'Your username is too short'),
        ('test', '', b'Your password is required'),
        ('test', 'test', b'Your password must at least 8 characters, and contain an upper case letter, a lower case letter and a digit'),
        ('hameshP', 'Test#6^0', b'Your username is already taken - please supply another'),
))


def test_register_with_invalid_input(client, username, password, message):
    client.post(
        '/authentication/register',
        data={'username': 'hameshP', 'password': 'HameshPatel123'}
    )
    response = client.post(
        '/authentication/register',
        data={'username': username, 'password': password}
    )
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'CompSci 235 Flix' in response.data


def test_login_required_to_comment(client):
    response = client.post('/review')
    assert response.headers['Location'] == 'http://localhost/authentication/login'


def test_movies_without_rank(client):
    response = client.get('/movies_by_rank')
    assert response.status_code == 200

    assert b'Ridley Scott' in response.data
    assert b'Prometheus' in response.data


def test_movies_with_rank(client):
    response = client.get('/movies_by_rank?id=10')

    assert response.status_code == 200

    assert b'Chris Pratt' in response.data
    assert b'Guardians of the Galaxy' in response.data


def test_movies_with_genre(client):
    response = client.get('/movies_by_genre?genre=Comedy')
    assert response.status_code == 200

    assert b'Comedy Movies' in response.data
    assert b'La La Land' in response.data
