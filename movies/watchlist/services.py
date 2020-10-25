from movies.adapters.repository import AbstractRepository
from movies.domain.model1 import make_review, Movie, Review, Actor, Director, Genre, User


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_to_watchlist(movie_id: int, username: str, repo: AbstractRepository):
    movie = repo.get_movie(movie_id)
    # if movie is None:
    #     raise NonExistentMovieException

    user = repo.get_user(username)
    # if user is None:
    #     raise UnknownUserException

    repo.add_to_watchlist(movie, user)


def get_watchlist(username: str, repo: AbstractRepository):
    user = repo.get_user(username)
    if user is None:
        raise UnknownUserException

    return user.watchlist


