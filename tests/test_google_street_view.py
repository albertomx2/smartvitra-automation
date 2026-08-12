from backend.integrations.google_maps.street_view import (
    GeoPoint,
    GoogleStreetViewFacadeClient,
)


def test_heading_points_towards_building():
    camera = GeoPoint(
        lat=40.4165611314066,
        lng=-3.704654982248522,
    )

    building = GeoPoint(
        lat=40.4163777,
        lng=-3.7045601,
    )

    heading = GoogleStreetViewFacadeClient.calculate_heading(
        origin=camera,
        target=building,
    )

    assert 158.0 < heading < 159.0


def test_heading_is_normalized():
    origin = GeoPoint(
        lat=40.0,
        lng=-3.0,
    )

    target = GeoPoint(
        lat=40.001,
        lng=-3.001,
    )

    heading = GoogleStreetViewFacadeClient.calculate_heading(
        origin=origin,
        target=target,
    )

    assert 0 <= heading < 360
