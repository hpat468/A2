import os
import pytest

from movies import create_app
from movies.adapters import memory_repository
from movies.adapters.memory_repository import MemoryRepository


TEST_DATA_PATH = os.path.join('C:', os.sep, 'Users', 'hpat468', 'Documents', 'CS235_hpat468', 'tests', 'data')


@pytest.fixture
def in_memory_repo():
    repo = MemoryRepository()
    memory_repository.populate(TEST_DATA_PATH, repo)
    return repo


@pytest.fixture
def client():
    my_app = create_app({
        'TESTING': True,
        'TEST_DATA_PATH': TEST_DATA_PATH,
        'WTF_CSRF_ENABLED': False
    })

    return my_app.test_client()


class AuthenticationManager:
    def __init__(self, client):
        self._client = client

    def login(self, username='hameshP', password='HameshPatel123'):
        self._client.post(
            'authentication/register',
            data={'username': username, 'password': password}
        )
        return self._client.post(
            'authentication/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthenticationManager(client)
