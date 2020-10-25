from werkzeug.security import generate_password_hash, check_password_hash

from movies.adapters.repository import AbstractRepository
from movies.domain.model1 import User


class NameNotUniqueException(Exception):
    pass


class UnknownUserException(Exception):
    pass


class AuthenticationException(Exception):
    pass


def add_user(username: str, password: str, repository: AbstractRepository):
    user = repository.get_user(username)
    if user is not None:
        raise NameNotUniqueException

    password_hash = generate_password_hash(password)

    user = User(username, password_hash)
    repository.add_user(user)


def get_user(username: str, repository: AbstractRepository):
    user = repository.get_user(username)
    if user is None:
        raise UnknownUserException

    return user_to_dict(user)


def authenticate_user(username: str, password: str, repository: AbstractRepository):
    authenticated = False

    user = repository.get_user(username)
    if user is not None:
        authenticated = check_password_hash(user.password, password)
    if not authenticated:
        raise AuthenticationException


def user_to_dict(user: User):
    user_dict = {
        'username': user.username,
        'password': user.password
    }
    return user_dict
