import pytest

from movies.domain.model1 import Movie, Genre, Director, Actor, Review, make_review, User
from movies.adapters.repository import RepositoryException


def test_repository_can_add_a_user(in_memory_repo):
    user = User('Jack', '123123123')
    in_memory_repo.add_user(user)

    assert in_memory_repo.get_user('Jack') is user


def test_repository_does_not_retrieve_a_non_existent_user(in_memory_repo):
    user = in_memory_repo.get_user('man')
    assert user is None


def test_repository_can_retrieve_movie_count(in_memory_repo):
    number_of_movies = in_memory_repo.get_number_of_movies()

    assert number_of_movies == 1000


def test_repository_can_add_movie(in_memory_repo):
    movie = Movie(
        "Compsci235 The Movie",
        2020
    )
    in_memory_repo.add_movie(movie)
    assert in_memory_repo.get_movie(1001) is movie


def test_repository_can_retrieve_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(2)

    assert movie.title == 'Prometheus'
    assert movie.genres == [Genre("Adventure"), Genre("Mystery"), Genre("Sci-Fi")]
    assert movie.director == Director("Ridley Scott")
    assert movie.actors == [Actor("Noomi Rapace"), Actor("Logan Marshall-Green"), Actor("Michael Fassbender"), Actor("Charlize Theron")]
    assert movie.year == 2012
    assert len(movie.reviews) == 0

def test_repository_does_not_retrieve_a_non_existent_movie(in_memory_repo):
    movie = in_memory_repo.get_movie(2000)
    assert movie is None


def test_repository_can_retrieve_movies_by_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(2014)

    assert len(movies) == 98


def test_repository_does_not_retrieve_a_movie_when_there_are_no_movies_for_a_given_year(in_memory_repo):
    movies = in_memory_repo.get_movies_by_year(1800)
    assert len(movies) == 0


def test_repository_can_get_first_movie(in_memory_repo):
    movie = in_memory_repo.get_first_movie()
    assert movie.title == 'Guardians of the Galaxy'


def test_repository_can_get_last_movie(in_memory_repo):
    movie = in_memory_repo.get_last_movie()
    assert movie.title == 'Nine Lives'


def test_repository_can_get_movies_by_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([2, 5, 6])

    assert len(movies) == 3
    assert movies[
               0].title == 'Prometheus'
    assert movies[1].title == "Split"
    assert movies[2].title == 'The Secret Life of Pets'


def test_repository_does_not_retrieve_movie_for_non_existent_id(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([0, 2, 5000])

    assert len(movies) == 1
    assert movies[
               0].title == 'Prometheus'


def test_repository_returns_an_empty_list_for_non_existent_ids(in_memory_repo):
    movies = in_memory_repo.get_movies_by_id([0, 5000])

    assert len(movies) == 0


def test_repository_returns_movie_ids_for_existing_actor(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_actor('Russell Crowe')
    movie_ids.sort()
    assert movie_ids == [96, 246, 388, 471, 531, 719, 738]


def test_repository_returns_an_empty_list_for_non_existent_actor(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_actor('Pam Su')

    assert len(movie_ids) == 0

def test_repository_returns_movie_ids_for_existing_director(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_director('James Gunn')
    movie_ids.sort()
    assert movie_ids == [1, 909, 938]


def test_repository_returns_an_empty_list_for_non_existent_director(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_director('Pam Su')

    assert len(movie_ids) == 0

def test_repository_returns_movie_ids_for_existing_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_genre('Comedy')
    movie_ids.sort()
    assert movie_ids == [78, 114, 161, 187, 231, 241, 480, 511, 644, 714, 763, 821, 895]


def test_repository_returns_an_empty_list_for_non_existent_genre(in_memory_repo):
    movie_ids = in_memory_repo.get_movie_ids_for_genre('Cow')

    assert len(movie_ids) == 0


def test_repository_can_add_a_review(in_memory_repo):
    user = User('Kate', '987654321')
    in_memory_repo.add_user(user)
    user = in_memory_repo.get_user('Kate')
    movie = in_memory_repo.get_movie(2)
    review = make_review(review_text="This movie was average", user=user, movie= movie)

    in_memory_repo.add_review(review)

    assert review in in_memory_repo.get_reviews()


def test_repository_does_not_add_a_review_without_a_user(in_memory_repo):
    movie = in_memory_repo.get_movie(2)
    review = Review(None, movie, "I like this movie :)")

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_does_not_add_a_review_without_a_movie_properly_attached(in_memory_repo):
    user = User('Kate', '987654321')
    in_memory_repo.add_user(user)
    user = in_memory_repo.get_user('Kate')
    movie = in_memory_repo.get_movie(2)
    review = Review(None, movie, "I recommend this movie to watch :)")

    user.add_review(review)

    with pytest.raises(RepositoryException):
        in_memory_repo.add_review(review)


def test_repository_can_retrieve_reviews(in_memory_repo):
    assert len(in_memory_repo.get_reviews()) == 0
    user = User('Kate', '987654321')
    in_memory_repo.add_user(user)
    user = in_memory_repo.get_user('Kate')
    movie = in_memory_repo.get_movie(2)
    review = make_review(review_text="This movie was great", user=user, movie=movie)

    in_memory_repo.add_review(review)
    assert len(in_memory_repo.get_reviews()) == 1


