from dataclasses import dataclass
from functools import reduce


@dataclass(frozen=True)
class Movie:
    """Ein Film mit Dauer in Minuten und eigener Bewertung von 0 bis 10."""

    id: int
    title: str
    genre: str
    duration: int
    rating: float


def create_movie(data: dict, movie_id: int) -> Movie:
    if not isinstance(data, dict):
        raise ValueError('Bitte ein JSON-Objekt mit Filmdaten senden.')

    title = data.get('title')
    genre = data.get('genre')
    duration = data.get('duration')
    rating = data.get('rating')

    if not isinstance(title, str) or not title.strip():
        raise ValueError('Der Titel darf nicht leer sein.')
    if not isinstance(genre, str) or not genre.strip():
        raise ValueError('Das Genre darf nicht leer sein.')
    if type(duration) is not int or duration <= 0:
        raise ValueError('Die Dauer muss eine positive ganze Zahl sein.')
    if type(rating) not in (int, float) or not 0 <= rating <= 10:
        raise ValueError('Die Bewertung muss eine Zahl von 0 bis 10 sein.')

    return Movie(movie_id, title.strip(), genre.strip(), duration, rating)


def filter_by_genre(movies: tuple[Movie, ...], genre: str) -> tuple[Movie, ...]:
    genre = genre.strip().casefold()
    if not genre:
        return movies
    return tuple(movie for movie in movies if movie.genre.casefold() == genre)


def movie_statistics(movies: tuple[Movie, ...], min_rating: float = 0) -> dict:
    ratings = ratings_at_least(movies, min_rating)
    return summarize_ratings(ratings)


def add_mutable(movies: list[Movie], movie: Movie) -> None:
    movies.append(movie)


def add_immutable(movies: tuple[Movie, ...], movie: Movie) -> tuple[Movie, ...]:
    return movies + (movie,)


def duration_procedural(movies: tuple[Movie, ...]) -> int:
    total = 0
    for movie in movies:
        total += movie.duration
    return total


def duration_functional(movies: tuple[Movie, ...]) -> int:
    return reduce(lambda total, movie: total + movie.duration, movies, 0)


class MovieCollection:

    def __init__(self, movies):
        self.movies = list(movies)

    def add(self, movie):
        add_mutable(self.movies, movie)

    def total_duration(self):
        return sum(movie.duration for movie in self.movies)


def duration_overview(movies: tuple[Movie, ...], style: str = 'functional') -> dict:
    duration = lambda movie: movie.duration
    durations = tuple(map(duration, movies))
    short_movies = tuple(filter(lambda movie: movie.duration <= 100, movies))
    if style == 'oo':
        total = MovieCollection(movies).total_duration()
    elif style == 'procedural':
        total = duration_procedural(movies)
    else:
        total = duration_functional(movies)
    return {'durations': durations,
            'short_titles': tuple(movie.title for movie in short_movies),
            'total_minutes': total}


def select_ids(movies: tuple[Movie, ...], ids: list[int]) -> tuple[Movie, ...]:
    selected_ids = set(ids)
    return tuple(movie for movie in movies if movie.id in selected_ids)


def rank_movies(movies: tuple[Movie, ...]) -> tuple[Movie, ...]:
    return tuple(sorted(movies, key=lambda movie: (-movie.rating, movie.title.casefold())))


def ratings_at_least(movies: tuple[Movie, ...], minimum: float) -> tuple[float, ...]:
    selected = filter(lambda movie: movie.rating >= minimum, movies)
    return tuple(map(lambda movie: movie.rating, selected))


def summarize_ratings(ratings: tuple[float, ...]) -> dict:
    total = reduce(lambda total, rating: total + rating, ratings, 0)
    average = total / len(ratings) if ratings else 0
    return {'count': len(ratings), 'average': average}
