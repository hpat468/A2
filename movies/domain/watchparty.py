from domainmodel.movie import Movie
from domainmodel.user import User
from domainmodel.review import Review

class WatchParty:
    def __init__(self, movie: Movie, members: list):
        self.__movie = movie
        self.__members = members
        # Update profiles
        for user in members:
            user.watch_movie(movie)
        self.__chatroom = []
        self.__group_review = None
        self.__individual_ratings = []

    def invite_member(self, user: User):
        if user not in self.__members:
            self.__members.append(user)
            user.watch_movie(self.__movie)

    def message_chatroom(self, user: User, message: str):
        self.__chatroom.append(f"{user.user_name}: {message}")

    def view_chatroom(self):
        return self.__chatroom

    def write_group_review(self, rating: int, review_text: str):
        self.__individual_ratings.append(rating)
        self.__group_review = Review(self.__movie, rating, review_text)
        for user in self.__members:
            user.add_review(self.__group_review)

    def add_to_group_review(self, rating: int, review_text: str):
        self.__individual_ratings.append(rating)
        new_review_text = f"{self.__group_review.review_text}. {review_text}"
        new_rating = sum(self.__individual_ratings) / len(self.__individual_ratings)
        self.__group_review = Review(self.__movie, new_rating, new_review_text)
        for user in self.__members:
            user.update_last_review(self.__group_review)

    def __repr__(self):
        if len(self.__members) == 0:
            return f"Watch party for {self.__movie.title}"
        elif len(self.__members) == 1:
            return f"{self.__members[0].user_name} is watching {self.__movie.title}"
        else:
            string = ""
            for i in range(0, len(self.__members) - 1):
                string += f"{self.__members[i].user_name}, "
            string += f"and {self.__members[-1].user_name} are watching {self.__movie.title}"
            return string

    def __eq__(self, other):
        return sorted(self.__members) == sorted(other.__members) and self.__movie == other.__movie

    def __lt__(self, other):
        return len(self.__members) < len(other.__members)

    @property
    def movie(self):
        return self.__movie

    @property
    def members(self):
        return self.__members

    @property
    def review(self):
        if type(self.__group_review) == Review:
            return f"Rating: {self.__group_review.rating}, Review: {self.__group_review.review_text}"
        else:
            return "No review given"
