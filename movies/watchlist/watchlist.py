from flask import Blueprint
from flask import request, render_template, redirect, url_for, session, flash

from flask_wtf import FlaskForm
from wtforms import TextAreaField, HiddenField, SubmitField, Form, StringField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError

import movies.adapters.repository as repo
import movies.movie_library.movie_library as movie_library
import movies.watchlist.services as services
import movies.utilities.utilities as utilities

from movies.authentication.authentication import login_required

watchlist_blueprint = Blueprint(
    'watchlist_bp', __name__)

@watchlist_blueprint.route('/add_watchlist', methods=['GET', "POST"])
@login_required
def add_to_watchlist():
    # Obtain the username of the currently logged in user.
    username = session['username']
    movie_id = request.args.get('movie')
    services.add_to_watchlist(movie_id, username, repo.repo_instance)

@watchlist_blueprint.route('/watchlist', methods=['GET', "POST"])
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
    movies = user_watchlist

    first_movie_url = None
    last_movie_url = None
    next_movie_url = None
    prev_movie_url = None

    if cursor > 0:
        # There are preceding movies, so generate URLs for the 'previous' and 'first' navigation buttons.
        prev_movie_url = url_for('watchlist_bp.watchlist', cursor=cursor - movies_per_page)
        first_movie_url = url_for('watchlist_bp.watchlist')

    if cursor + movies_per_page < len(movies):
        # There are further movies, so generate URLs for the 'next' and 'last' navigation buttons.
        next_movie_url = url_for('watchlist_bp.watchlist', cursor=cursor + movies_per_page)

        last_cursor = movies_per_page * int(len(movies) / movies_per_page)
        if len(movies) % movies_per_page == 0:
            last_cursor -= movies_per_page
        last_movie_url = url_for('watchlist_bp.watchlist', cursor=last_cursor)

    # Construct urls for viewing movie reviews and adding reviews.
    for movie in movies:
        movie['view_review_url'] = url_for('watchlist_bp.watchlist', cursor=cursor, view_reviews_for = movie['id'])
        movie['add_review_url'] = url_for('movie_library_bp.write_review_on_movie', movie=movie['id'])
        movie['add_to_watchlist_url'] = url_for('watchlist_bp.add_to_watchlist', movie=movie['id'])
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
        show_reviews_for_movie=movie_to_show_reviews
    )




