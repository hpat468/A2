from typing import Iterable

from movies.adapters.repository import AbstractRepository
from movies.domain.model1 import make_review, Movie, Review


class NonExistentMovieException(Exception):
    pass


class UnknownUserException(Exception):
    pass


def add_review(movie_id: int, review_text: str, username: str, repository: AbstractRepository):
    movie = repository.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    user = repository.get_user(username)
    if user is None:
        raise UnknownUserException

    review = make_review(review_text=review_text, user=user, movie=movie)
    repository.add_review(review)
    return review_to_dict(review)


def get_movie(movie_id: int, repository: AbstractRepository):
    movie = repository.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    return movie_to_dict(movie)


def get_first_movie(repository: AbstractRepository):
    movie = repository.get_first_movie()
    return movie_to_dict(movie)


def get_last_movie(repository: AbstractRepository):
    movie = repository.get_last_movie()
    return movie_to_dict(movie)


def add_to_watchlist(movie_id: int, username: str, repository: AbstractRepository):
    movie = repository.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    user = repository.get_user(username)
    if user is None:
        raise UnknownUserException
    repository.add_to_watchlist(movie, user)


def remove_from_watchlist(movie_id: int, username: str, repository: AbstractRepository):

    movie = repository.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    user = repository.get_user(username)
    if user is None:
        raise UnknownUserException

    repository.remove_from_watchlist(movie, user)


def get_watchlist(username: str, repository: AbstractRepository):
    user = repository.get_user(username)
    if user is None:
        raise UnknownUserException

    return user.watchlist


def get_movies_by_rank(id, repository: AbstractRepository):
    id_list = [id]
    movies = repository.get_movies_by_id(id_list)

    movies_dto = list()
    prev_id = next_id = None

    if len(movies) > 0:
        prev_id = repository.get_id_of_previous_movie(movies[0])
        next_id = repository.get_id_of_next_movie(movies[0])

        # Convert Movies to dictionary form.
        movies_dto = movies_to_dict(movies)

    return movies_dto, prev_id, next_id


def get_movie_ids_for_actor(actor_name, repository: AbstractRepository):
    movie_ids = repository.get_movie_ids_for_actor(actor_name)
    return movie_ids


def get_movie_ids_for_director(director_name, repository: AbstractRepository):
    director_ids = repository.get_movie_ids_for_director(director_name)
    return director_ids


def get_movie_ids_for_genre(genre_name, repository: AbstractRepository):
    genre_ids = repository.get_movie_ids_for_genre(genre_name)
    return genre_ids


def get_movies_by_id(id_list, repository: AbstractRepository):
    movies = repository.get_movies_by_id(id_list)
    movies_as_dict = movies_to_dict(movies)
    return movies_as_dict


def get_reviews_for_movie(movie_id, repository: AbstractRepository):
    movie = repository.get_movie(movie_id)
    if movie is None:
        raise NonExistentMovieException

    return reviews_to_dict(movie.reviews)


def movie_to_dict(movie: Movie):
    movie_dict = {
        'id': movie.id,
        'year': movie.year,
        'title': movie.title,
        'reviews': reviews_to_dict(movie.reviews),
        'actors': movie.actors,
        'director': movie.director,
        'genres': movie.genres,
        "description": movie.description,
        "imagelink": movie.imagelink
    }
    return movie_dict


def movies_to_dict(movies: Iterable[Movie]):
    return [movie_to_dict(movie) for movie in movies]


def review_to_dict(review: Review):
    review_dict = {
        'username': review.user.username,
        'movie_id': review.movie.id,
        'review_text': review.review_text,
        'timestamp': review.timestamp
    }
    return review_dict


def reviews_to_dict(reviews: Iterable[Review]):
    return [review_to_dict(review) for review in reviews]


def dict_to_movie(dictionary):
    movie = Movie(dictionary.title, dictionary.year)
    movie.add_id(dictionary.id)
    return movie
