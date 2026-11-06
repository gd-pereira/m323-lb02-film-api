"""Film-API auf Basis von LU06-A02."""

from dataclasses import asdict

from flask import Flask, jsonify, request

from movie import (
    Movie, MovieCollection, add_immutable, create_movie, filter_by_genre,
    movie_statistics, duration_overview, select_ids, rank_movies,
)

app = Flask(__name__)

movies = (
    Movie(1, 'Film A', 'Drama', 100, 6),
    Movie(2, 'Film B', 'Action', 120, 8),
    Movie(3, 'Film C', 'Drama', 90, 10),
)


@app.route('/movies', methods=['GET'])
def movie_overview():
    genre = request.args.get('genre', '')
    selected_movies = filter_by_genre(movies, genre)
    return jsonify([asdict(movie) for movie in selected_movies])


@app.route('/movies', methods=['POST'])
def add_movie():
    global movies
    data = request.get_json(silent=True)
    new_id = max((movie.id for movie in movies), default=0) + 1
    try:
        movie = create_movie(data, new_id)
    except ValueError as error:
        return jsonify({'error': str(error)}), 400

    if request.args.get('style') == 'oo':
        collection = MovieCollection(movies)
        collection.add(movie)
        movies = tuple(collection.movies)
    else:
        movies = add_immutable(movies, movie)
    return jsonify(asdict(movie)), 201


@app.route('/movies/stats', methods=['GET'])
def statistics():
    try:
        min_rating = float(request.args.get('min_rating', 0))
        if not 0 <= min_rating <= 10:
            raise ValueError
    except ValueError:
        return jsonify({'error': 'Die Mindestbewertung muss eine Zahl von 0 bis 10 sein.'}), 400
    return jsonify(movie_statistics(movies, min_rating))


@app.route('/movies/duration', methods=['GET'])
def duration():
    style = request.args.get('style', 'functional')
    if style not in ('functional', 'procedural', 'oo'):
        return jsonify({'error': 'Unbekannte Variante.'}), 400
    return jsonify(duration_overview(movies, style))


@app.route('/movies/ranking', methods=['GET'])
def ranking():
    selected = movies
    if 'ids' in request.args:
        try:
            ids = [int(value) for value in request.args['ids'].split(',') if value]
        except ValueError:
            return jsonify({'error': 'IDs müssen ganze Zahlen sein.'}), 400
        selected = select_ids(movies, ids)
    return jsonify([asdict(movie) for movie in rank_movies(selected)])


if __name__ == '__main__':
    app.run()
