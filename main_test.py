import pytest

import main


@pytest.fixture
def client():
    saved_movies = main.movies
    main.app.config['TESTING'] = True
    with main.app.test_client() as test_client:
        yield test_client
    main.movies = saved_movies


def test_movie_overview(client):
    response = client.get('/movies')
    assert response.status_code == 200
    assert [movie['title'] for movie in response.get_json()] == [
        'Film A', 'Film B', 'Film C',
    ]


def test_genre_filter(client):
    response = client.get('/movies?genre=Drama')
    assert response.status_code == 200
    assert [movie['title'] for movie in response.get_json()] == ['Film A', 'Film C']
    assert len(client.get('/movies').get_json()) == 3


def test_unknown_genre(client):
    response = client.get('/movies?genre=Comedy')
    assert response.status_code == 200
    assert response.get_json() == []


def test_add_movie(client):
    data = {'title': 'Film D', 'genre': 'Comedy', 'duration': 95, 'rating': 7.5}
    response = client.post('/movies', json=data)
    expected = {'id': 4, **data}
    assert response.status_code == 201
    assert response.get_json() == expected
    assert client.get('/movies').get_json()[-1] == expected


def test_invalid_movie(client):
    data = {'title': 'Film D', 'genre': 'Comedy', 'duration': 95, 'rating': 11}
    response = client.post('/movies', json=data)
    assert response.status_code == 400
    assert response.get_json()['error']
    assert len(client.get('/movies').get_json()) == 3


def test_statistics(client):
    response = client.get('/movies/stats?min_rating=8')
    assert response.status_code == 200
    assert response.get_json() == {'count': 2, 'average': 9}
    assert client.get('/movies/stats').get_json() == {'count': 3, 'average': 8}


def test_statistics_no_matches(client):
    main.movies = main.movies[:2]
    response = client.get('/movies/stats?min_rating=9')
    assert response.status_code == 200
    assert response.get_json() == {'count': 0, 'average': 0}


def test_statistics_invalid_filter(client):
    response = client.get('/movies/stats?min_rating=abc')
    assert response.status_code == 400
    assert response.get_json()['error']


def test_ranking(client):
    response = client.get('/movies/ranking')
    assert response.status_code == 200
    assert [movie['id'] for movie in response.get_json()] == [3, 2, 1]
    main.movies = (main.Movie(1, 'Z', 'Drama', 100, 8),
                   main.Movie(2, 'A', 'Drama', 100, 8))
    assert [movie['id'] for movie in client.get('/movies/ranking').get_json()] == [2, 1]


def test_ranking_selection(client):
    response = client.get('/movies/ranking?ids=1,3,1,99')
    assert [movie['id'] for movie in response.get_json()] == [3, 1]
    assert client.get('/movies/ranking?ids=').get_json() == []
    assert client.get('/movies/ranking?ids=abc').status_code == 400


def test_duration_variants(client):
    expected = {'durations': [100, 120, 90], 'short_titles': ['Film A', 'Film C'],
                'total_minutes': 310}
    for style in ('functional', 'procedural', 'oo'):
        response = client.get('/movies/duration', query_string={'style': style})
        assert response.status_code == 200
        assert response.get_json() == expected


def test_empty_duration_and_ranking(client):
    main.movies = ()
    for style in ('functional', 'procedural', 'oo'):
        assert client.get('/movies/duration', query_string={'style': style}).get_json() == {
            'durations': [], 'short_titles': [], 'total_minutes': 0}
    assert client.get('/movies/ranking').get_json() == []


def test_mutable_and_immutable_addition():
    from movie import add_mutable, add_immutable
    movie = main.Movie(4, 'Film D', 'Comedy', 95, 7.5)
    items = list(main.movies)
    alias = items
    assert add_mutable(items, movie) is None
    assert alias[-1] == movie
    before = main.movies
    after = add_immutable(before, movie)
    assert len(before) == 3 and len(after) == 4
    assert before is main.movies and after is not before


def test_add_oo_variant(client):
    data = {'title': 'Film D', 'genre': 'Comedy', 'duration': 95, 'rating': 7.5}
    response = client.post('/movies?style=oo', json=data)
    assert response.status_code == 201
    assert response.get_json() == {'id': 4, **data}
    assert len(client.get('/movies').get_json()) == 4
