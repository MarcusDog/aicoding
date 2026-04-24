from app.utils.location import haversine


def test_haversine_same_point():
    assert haversine(31.0, 121.0, 31.0, 121.0) == 0


def test_haversine_rough_distance():
    distance = haversine(0.0, 0.0, 1.0, 0.0)
    assert 110000 <= distance <= 112500
