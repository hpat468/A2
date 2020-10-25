from domainmodel.movie import Movie

class WatchList:
    def __init__(self):
        self.__watch_list = []
    def add_movie(self, movie: Movie):
        if movie not in self.__watch_list:
            self.__watch_list.append(movie)
    def remove_movie(self, movie: Movie):
        if movie in self.__watch_list:
            for i in range(len(self.__watch_list)):
                if self.__watch_list[i] == movie:
                    self.__watch_list.pop(i)
    def select_movie_to_watch(self, index: int):
        if index >= 0 and index < len(self.__watch_list):
            return self.__watch_list[index]
        else:
            return None
    def size(self):
        return len(self.__watch_list)
    def first_movie_in_watchlist(self):
        if len(self.__watch_list) == 0:
            return None
        else:
            return self.__watch_list[0]

    def __iter__(self):
        self.n = 0
        return self

    def __next__(self):
        if self.n < len(self.__watch_list):
            result = self.__watch_list[self.n]
            self.n += 1
            return result
        else:
            raise StopIteration

class TestWatchlist:
    def test_init(self):
        # Test first_movie_in_watchlist()
        watchlist1 = WatchList()
        assert watchlist1.first_movie_in_watchlist() == None
        assert watchlist1.size() == 0
        assert watchlist1.select_movie_to_watch(5) == None
        watchlist1.add_movie(Movie("Life Of Pi", 2012))
        assert repr(watchlist1.first_movie_in_watchlist()) == "<Movie Life Of Pi, 2012>"
        assert watchlist1.size() == 1
        watchlist1.add_movie(Movie("Ice Age", 2002))
        watchlist1.add_movie(Movie("Guardians of the Galaxy", 2012))
        assert repr(watchlist1.first_movie_in_watchlist()) == "<Movie Life Of Pi, 2012>"
        assert watchlist1.size() == 3
        assert repr(watchlist1.select_movie_to_watch(0)) == "<Movie Life Of Pi, 2012>"
        assert watchlist1.select_movie_to_watch(15) == None
        assert repr(watchlist1.select_movie_to_watch(1)) == "<Movie Ice Age, 2002>"