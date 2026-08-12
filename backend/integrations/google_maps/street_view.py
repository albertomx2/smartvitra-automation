import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


@dataclass(frozen=True)
class GeoPoint:
    lat: float
    lng: float


@dataclass(frozen=True)
class StreetViewPanorama:
    pano_id: str

    location: GeoPoint

    date: str | None = None


class GoogleStreetViewFacadeClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout: int = 20,
    ) -> None:
        resolved_api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")

        if not resolved_api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY " "is required")

        self._api_key = resolved_api_key

        self._timeout = timeout

    def download_facade(
        self,
        *,
        address: str,
        output_path: Path,
        size: str = "640x640",
        fov: int = 80,
        pitch: int = 5,
    ) -> Path:
        building = self.geocode(address)

        panorama = self.find_panorama(building)

        heading = self.calculate_heading(
            origin=panorama.location,
            target=building,
        )

        params = urlencode(
            {
                "size": size,
                "pano": panorama.pano_id,
                "heading": (f"{heading:.2f}"),
                "pitch": str(pitch),
                "fov": str(fov),
                "return_error_code": ("true"),
                "key": self._api_key,
            }
        )

        url = "https://maps.googleapis.com/" "maps/api/streetview?" + params

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with urlopen(
            url,
            timeout=self._timeout,
        ) as response:
            content_type = response.headers.get(
                "Content-Type",
                "",
            )

            if "image/" not in content_type:
                raise RuntimeError("Street View did not " "return an image")

            output_path.write_bytes(response.read())

        return output_path

    def geocode(
        self,
        address: str,
    ) -> GeoPoint:
        params = urlencode(
            {
                "address": address,
                "key": self._api_key,
            }
        )

        url = "https://maps.googleapis.com/" "maps/api/geocode/json?" + params

        with urlopen(
            url,
            timeout=self._timeout,
        ) as response:
            data = json.load(response)

        status = data.get("status")

        if status != "OK":
            raise RuntimeError("Geocoding failed: " f"{status}")

        results = data.get(
            "results",
            [],
        )

        if not results:
            raise RuntimeError("Geocoding returned " "no results")

        location = results[0]["geometry"]["location"]

        return GeoPoint(
            lat=float(location["lat"]),
            lng=float(location["lng"]),
        )

    def find_panorama(
        self,
        location: GeoPoint,
    ) -> StreetViewPanorama:
        params = urlencode(
            {
                "location": (f"{location.lat}," f"{location.lng}"),
                "source": "outdoor",
                "key": self._api_key,
            }
        )

        url = "https://maps.googleapis.com/" "maps/api/streetview/" "metadata?" + params

        with urlopen(
            url,
            timeout=self._timeout,
        ) as response:
            data = json.load(response)

        status = data.get("status")

        if status != "OK":
            raise RuntimeError("Street View metadata " "failed: " f"{status}")

        location_data = data.get("location")

        pano_id = data.get("pano_id")

        if location_data is None or pano_id is None:
            raise RuntimeError("Street View panorama " "data incomplete")

        return StreetViewPanorama(
            pano_id=pano_id,
            location=GeoPoint(
                lat=float(location_data["lat"]),
                lng=float(location_data["lng"]),
            ),
            date=data.get("date"),
        )

    @staticmethod
    def calculate_heading(
        *,
        origin: GeoPoint,
        target: GeoPoint,
    ) -> float:
        lat1 = math.radians(origin.lat)

        lat2 = math.radians(target.lat)

        delta_lng = math.radians(target.lng - origin.lng)

        x = math.sin(delta_lng) * math.cos(lat2)

        y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(
            lat2
        ) * math.cos(delta_lng)

        return (
            math.degrees(
                math.atan2(
                    x,
                    y,
                )
            )
            + 360
        ) % 360
