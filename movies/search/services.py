from movies.adapters.repository import AbstractRepository
from movies.domain.model1 import Actor, Director, Genre


def search_exists(search, select, repository: AbstractRepository):
    genres = repository.get_genres()
    actors = repository.get_actors()
    directors = repository.get_directors()
    if select == "Actor":
        if Actor(search) not in actors:
            return False
        else:
            return True
    elif select == "Director":
        if Director(search) not in directors:
            return False
        else:
            return True
    elif select == "Genre":
        if Genre(search) not in genres:
            return False
        else:
            return True
