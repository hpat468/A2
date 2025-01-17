"""Initialize Flask app"""

import os

from flask import Flask

import movies.adapters.repository as repo
from movies.adapters.memory_repository import MemoryRepository, populate


def create_app(test_config=None):
    """Construct the core application."""

    # Create the Flask app object.
    app = Flask(__name__)

    app.config.from_object('config.Config')
    data_path = os.path.join('movies', 'adapters', 'data')

    if test_config is not None:
        app.config.from_mapping(test_config)
        data_path = app.config['TEST_DATA_PATH']

    repo.repo_instance = MemoryRepository()
    populate(data_path, repo.repo_instance)

    with app.app_context():
        # Register blueprints.
        from .home import home
        app.register_blueprint(home.home_blueprint)

        from .movie_library import movie_library
        app.register_blueprint(movie_library.movie_library_blueprint)

        from .authentication import authentication
        app.register_blueprint(authentication.authentication_blueprint)

        from .utilities import utilities
        app.register_blueprint(utilities.utilities_blueprint)

        from .search import search
        app.register_blueprint(search.search_blueprint)

    return app
