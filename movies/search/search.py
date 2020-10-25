from flask import Blueprint
from flask import request, render_template, redirect, url_for, flash
from wtforms import Form, StringField, SelectField


import movies.adapters.repository as repo
import movies.search.services as services

search_blueprint = Blueprint('search_bp', __name__)


@search_blueprint.route('/search', methods=['GET', 'POST'])
def search():
    search = MovieSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search.data['search'], search.data['select'])

    return render_template('search/search.html',
                           form=search,
                           title="Search Movies",
                           description="Search for movies by actor, genre or director")


@search_blueprint.route('/results')
def search_results(search, select):
    search = search.title()
    search_exists = services.search_exists(search, select, repo.repo_instance)
    if search_exists:
        if select == "Actor":
            return redirect(url_for('movie_library_bp.movies_by_actor', actor=search))
        elif select == "Director":
            return redirect(url_for('movie_library_bp.movies_by_director', director=search))
        elif select == "Genre":
            return redirect(url_for('movie_library_bp.movies_by_genre', genre=search))
    else:
        flash('No results found!')
        return redirect(url_for('search_bp.search'))


class MovieSearchForm(Form):
    choices = [('Actor', 'Actor'),
               ('Director', 'Director'),
               ('Genre', 'Genre')]
    select = SelectField('Search for movie:', choices=choices)
    search = StringField('')