from datetime import date

from flask import Blueprint
from flask import request, render_template, redirect, url_for, session

from better_profanity import profanity
from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, Form, StringField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

import movies.adapters.repository as repo
import movies.utilities.utilities as utilities
import movies.movie_library.services as services

from movies.authentication.authentication import login_required

# Configure Blueprint.
movie_library_blueprint = Blueprint(
    'movie_library_bp', __name__)


@movie_library_blueprint.route('/movies_by_rank', methods=['GET'])
def movies_by_rank():
    # Read query parameters.
    target_id = request.args.get('id')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    # Fetch the first and last movies in the series.
    first_movie = services.get_first_movie(repo.repo_instance)
    last_movie = services.get_last_movie(repo.repo_instance)

    if target_id is None:
        # No id query parameter, so return movies from day 1 of the series.
        target_id = first_movie['id']
    else:
        # Convert target_year from string to int.
        target_id = int(target_id)

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    # Fetch movie(s) for the target id. This call also returns the previous and next ids for movies immediately
    # before and after the target.
    movies, previous_id, next_id = services.get_movies_by_rank(target_id, repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if len(movies) > 0:
        # There's at least one movie for the target id.
        if previous_id is not None:
            # There are movie on a previous id, so generate URLs for the 'previous' and 'first' navigation buttons.
            prev_movie_url = url_for('movie_library_bp.movies_by_rank', id=previous_id)
            first_movie_url = url_for('movie_library_bp.movies_by_rank', id=first_movie['id'])

        # There are movies subsequent, so generate URLs for the 'next' and 'last' navigation buttons.
        if next_id is not None:
            next_movie_url = url_for('movie_library_bp.movies_by_rank', id=next_id)
            last_movie_url = url_for('movie_library_bp.movies_by_rank', id=last_movie['id'])

        # Construct urls for viewing movie reviews and adding reviews.
        for movie in movies:
            movie['view_review_url'] = url_for('movie_library_bp.movies_by_rank', id=target_id,
                                               view_reviews_for=movie['id'])
            movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
            movie['add_to_watchlist_url'] = url_for('movie_library_bp.add_to_watchlist', movie=movie['id'])
        # Generate the webpage to display the movies.
        return render_template(
            'movie_library/movies.html',
            title='Movies',
            movies_title="Ranked: " + str(target_id),
            movies=movies,
            selected_movies=utilities.get_selected_movies(3),
            actor_urls=utilities.get_actors_and_urls(),
            director_urls=utilities.get_directors_and_urls(),
            genre_urls=utilities.get_genres_and_urls(),
            first_movie_url=first_movie_url,
            last_movie_url=last_movie_url,
            prev_movie_url=prev_movie_url,
            next_movie_url=next_movie_url,
            show_reviews_for_movie=movie_to_show_reviews,
            is_watchlist=False
        )

    # No movies to show, so return the homepage.
    return redirect(url_for('home_bp.home'))


@movie_library_blueprint.route('/movies_by_actor', methods=['GET'])
def movies_by_actor():
    movies_per_page = 3

    # Read query parameters.
    actor_name = request.args.get('actor')
    cursor = request.args.get('cursor')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that have actor_name.
    movie_ids = services.get_movie_ids_for_actor(actor_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movie_library_bp.movies_by_actor', actor=actor_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('movie_library_bp.movies_by_actor', actor=actor_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movie_library_bp.movies_by_actor', actor=actor_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movie_library_bp.movies_by_actor', actor=actor_name, cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('movie_library_bp.movies_by_actor', actor=actor_name, cursor=cursor,
                                           view_reviews_for=movie['id'])
        movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
        movie['add_to_watchlist_url'] = url_for('movie_library_bp.add_to_watchlist', movie=movie['id'])
    # Generate the webpage to display the movies.
    return render_template(
        'movie_library/movies.html',
        title='Movies',
        movies_title='Movies featuring ' + actor_name,
        movies=movies,
        selected_movies=utilities.get_selected_movies(3),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_reviews,
        is_watchlist=False
    )


@movie_library_blueprint.route('/movies_by_genre', methods=['GET'])
def movies_by_genre():
    movies_per_page = 3

    # Read query parameters.
    genre_name = request.args.get('genre')
    cursor = request.args.get('cursor')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that have genre_name.
    movie_ids = services.get_movie_ids_for_genre(genre_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movie_library_bp.movies_by_genre', genre=genre_name, cursor=cursor - movies_per_page)
        first_movie_url = url_for('movie_library_bp.movies_by_genre', genre=genre_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movie_library_bp.movies_by_genre', genre=genre_name, cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movie_library_bp.movies_by_genre', genre=genre_name, cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('movie_library_bp.movies_by_genre', genre=genre_name, cursor=cursor,
                                           view_reviews_for=movie['id'])
        movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
        movie['add_to_watchlist_url'] = url_for('movie_library_bp.add_to_watchlist', movie=movie['id'])

    # Generate the webpage to display the movies.
    return render_template(
        'movie_library/movies.html',
        title='Movies',
        movies_title=genre_name + ' Movies',
        movies=movies,
        selected_movies=utilities.get_selected_movies(3),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_reviews,
        is_watchlist=False
    )


@movie_library_blueprint.route('/movies_by_director', methods=['GET'])
def movies_by_director():
    movies_per_page = 3

    # Read query parameters.
    director_name = request.args.get('director')
    cursor = request.args.get('cursor')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve movie ids for movies that have director_name.
    movie_ids = services.get_movie_ids_for_director(director_name, repo.repo_instance)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.get_movies_by_id(movie_ids[cursor:cursor + movies_per_page], repo.repo_instance)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movie_library_bp.movies_by_director', director=director_name,
                                 cursor=cursor - movies_per_page)
        first_movie_url = url_for('movie_library_bp.movies_by_director', director=director_name)

    if cursor + movies_per_page < len(movie_ids):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movie_library_bp.movies_by_director', director=director_name,
                                 cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movie_ids) / movies_per_page)
        if len(movie_ids) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movie_library_bp.movies_by_director', director=director_name, cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('movie_library_bp.movies_by_director', director=director_name, cursor=cursor,
                                           view_reviews_for=movie['id'])
        movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
        movie['add_to_watchlist_url'] = url_for('movie_library_bp.add_to_watchlist', movie=movie['id'])
    # Generate the webpage to display the movies.
    return render_template(
        'movie_library/movies.html',
        title='Movies',
        movies_title='Movies directed by ' + director_name,
        movies=movies,
        selected_movies=utilities.get_selected_movies(3),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_reviews,
        is_watchlist=False
    )


@movie_library_blueprint.route('/review', methods=['GET', 'POST'])
@login_required
def write_review_on_movie():
    # Obtain the username of the currently logged in user.
    username = session['username']

    # Create form. The form maintains state, e.g. when this method is called with a HTTP GET request and populates
    # the form with a movie id, when subsequently called with a HTTP POST request, the movie id remains in the
    # form.
    form = ReviewForm()

    if form.validate_on_submit():
        # Successful POST, i.e. the review text has passed data validation.
        # Extract the movie id, representing the reviewed movie, from the form.
        movie_id = int(form.movie_id.data)

        # Use the service layer to store the new review.
        services.add_review(movie_id, form.review.data, username, repo.repo_instance)

        # Retrieve the movie in dict form.
        movie = services.get_movie(movie_id, repo.repo_instance)

        # display all reviews, including the new review.
        return redirect(url_for('movie_library_bp.movies_by_rank', id=movie_id, view_reviews_for=movie_id))

    if request.method == 'GET':
        # Request is a HTTP GET to display the form.
        # Extract the movie_id, representing the movie to review, from a query parameter of the GET request.
        movie_id = int(request.args.get('movie'))

        # Store the movie id in the form.
        form.movie_id.data = movie_id
    else:
        # Request is a HTTP POST where form validation has failed.
        # Extract the movie id of the movie being reviewed from the form.
        movie_id = int(form.movie_id.data)

    # For a GET or an unsuccessful POST, retrieve the movie to review in dict form, and return a Web page that allows
    # the user to enter a review. The generated Web page includes a form object.
    movie = services.get_movie(movie_id, repo.repo_instance)
    return render_template(
        'movie_library/write_review_for_movie.html',
        title='Edit Movie',
        movie=movie,
        form=form,
        handler_url=url_for('movie_library_bp.write_review_on_movie'),
    )


@movie_library_blueprint.route('/add_watchlist', methods=['GET'])
@login_required
def add_to_watchlist():
    # Obtain the username of the currently logged in user.
    m_id = request.args.get('movie')
    services.add_to_watchlist(int(m_id), session['username'], repo.repo_instance)
    return redirect(url_for('movie_library_bp.watchlist'))


@movie_library_blueprint.route('/remove_from_watchlist', methods=['GET'])
@login_required
def remove_from_watchlist():
    # Obtain the username of the currently logged in user.
    m_id = request.args.get('movie')
    services.remove_from_watchlist(int(m_id), session['username'], repo.repo_instance)
    return redirect(url_for('movie_library_bp.watchlist'))


@movie_library_blueprint.route('/watchlist', methods=['GET'])
@login_required
def watchlist():
    username = session['username']
    user_watchlist = services.get_watchlist(username, repo.repo_instance)

    movies_per_page = 3

    # Read query parameters.
    cursor = request.args.get('cursor')
    movie_to_show_reviews = request.args.get('view_reviews_for')

    if movie_to_show_reviews is None:
        # No view-reviews query parameter, so set to a non-existent movie id.
        movie_to_show_reviews = -1
    else:
        # Convert movie_to_show_reviews from string to int.
        movie_to_show_reviews = int(movie_to_show_reviews)

    if cursor is None:
        # No cursor query parameter, so initialise cursor to start at the beginning.
        cursor = 0
    else:
        # Convert cursor from string to int.
        cursor = int(cursor)

    # Retrieve the batch of movies to display on the Web page.
    movies = services.movies_to_dict(user_watchlist)

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('movie_library_bp.watchlist', cursor=cursor - movies_per_page)
        first_movie_url = url_for('movie_library_bp.watchlist')

    if cursor + movies_per_page < len(movies):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('movie_library_bp.watchlist', cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movies) / movies_per_page)
        if len(movies) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('movie_library_bp.watchlist', cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('movie_library_bp.watchlist', cursor=cursor, view_reviews_for=movie['id'])
        movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
        movie['add_to_watchlist_url'] = url_for('movie_library_bp.add_to_watchlist', movie=movie['id'])
        movie['remove_from_watchlist_url'] = url_for('movie_library_bp.remove_from_watchlist', movie=movie['id'])
    # Generate the webpage to display the movies.
    return render_template(
        'movie_library/movies.html',
        title='Movies',
        movies_title=username + "'s Watch List",
        movies=movies,
        selected_movies=utilities.get_selected_movies(3),
        actor_urls=utilities.get_actors_and_urls(),
        director_urls=utilities.get_directors_and_urls(),
        genre_urls=utilities.get_genres_and_urls(),
        first_movie_url=first_movie_url,
        last_movie_url=last_movie_url,
        prev_movie_url=prev_movie_url,
        next_movie_url=next_movie_url,
        show_reviews_for_movie=movie_to_show_reviews,
        is_watchlist=True
    )

class ProfanityFree:
    def __init__(self, message=None):
        if not message:
            message = u'Field must not contain profanity'
        self.message = message

    def __call__(self, form, field):
        if profanity.contains_profanity(field.data):
            raise ValidationError(self.message)


class ReviewForm(FlaskForm):
    review = TextAreaField('Review', [
        DataRequired(),
        Length(min=4, message='Your review is too short'),
        ProfanityFree(message='Your review must not contain profanity')])
    m_id = HiddenField("Movie id")
    submit = SubmitField('Submit')
