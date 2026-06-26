from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


LOCATION_DATA_PATH = Path(__file__).resolve().parent.parent / "knowledge" / "structured" / "birth-locations.json"


@dataclass(frozen=True)
class BirthLocation:
    id: str
    scope: str
    display_name: str
    latitude: float
    longitude: float
    timezone: str
    country: str = ""
    province: str = ""
    city: str = ""
    district: str = ""
    region: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "scope": self.scope,
            "display_name": self.display_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timezone": self.timezone,
            "country": self.country,
            "province": self.province,
            "city": self.city,
            "district": self.district,
            "region": self.region,
        }


@lru_cache(maxsize=1)
def load_birth_locations() -> dict[str, Any]:
    return json.loads(LOCATION_DATA_PATH.read_text(encoding="utf-8"))


def list_birth_locations() -> list[BirthLocation]:
    data = load_birth_locations()
    return [_location_from_dict(item) for item in data.get("locations", []) if isinstance(item, dict)]


def default_birth_location() -> BirthLocation:
    data = load_birth_locations()
    return resolve_birth_location(data.get("default_location_id"))


def resolve_birth_location(value: Any = None) -> BirthLocation:
    locations = list_birth_locations()
    by_id = {item.id: item for item in locations}
    if isinstance(value, dict):
        location_id = str(value.get("id") or "").strip()
        if location_id and location_id in by_id:
            return by_id[location_id]
        try:
            latitude = float(value.get("latitude"))
            longitude = float(value.get("longitude"))
        except Exception:
            latitude = longitude = math.nan
        timezone_name = str(value.get("timezone") or "").strip()
        if math.isfinite(latitude) and math.isfinite(longitude) and timezone_name:
            return BirthLocation(
                id=location_id or "custom",
                scope=str(value.get("scope") or "custom"),
                display_name=str(value.get("display_name") or value.get("name") or "自定义地区"),
                latitude=latitude,
                longitude=longitude,
                timezone=timezone_name,
                country=str(value.get("country") or ""),
                province=str(value.get("province") or ""),
                city=str(value.get("city") or ""),
                district=str(value.get("district") or ""),
                region=str(value.get("region") or ""),
            )
    text = str(value or "").strip()
    if text:
        if text in by_id:
            return by_id[text]
        lowered = text.lower()
        tokens = [token for token in lowered.split() if token]
        for item in locations:
            haystack = " ".join(
                [
                    item.id,
                    item.display_name,
                    item.country,
                    item.province,
                    item.city,
                    item.district,
                    item.region,
                ]
            ).lower()
            if lowered and lowered in haystack:
                return item
            if tokens and all(token in haystack for token in tokens):
                return item
    default_id = str(load_birth_locations().get("default_location_id") or "")
    return by_id.get(default_id) or locations[0]


def calculate_true_solar_time(standard_dt: datetime, location: BirthLocation) -> dict[str, Any]:
    tzinfo = ZoneInfo(location.timezone)
    local_dt = standard_dt.astimezone(tzinfo) if standard_dt.tzinfo else standard_dt.replace(tzinfo=tzinfo)
    central_longitude = _timezone_central_longitude(local_dt)
    longitude_minutes = (location.longitude - central_longitude) * 4
    equation_minutes = _equation_of_time_minutes(local_dt)
    total_minutes = longitude_minutes + equation_minutes
    true_dt = local_dt + timedelta(minutes=total_minutes)
    return {
        "standard_datetime": local_dt.isoformat(),
        "true_datetime": true_dt.isoformat(),
        "true_date": true_dt.strftime("%Y-%m-%d"),
        "true_time": true_dt.strftime("%H:%M"),
        "display_text": true_dt.strftime("%Y-%m-%d %H:%M"),
        "longitude_correction_minutes": round(longitude_minutes, 2),
        "equation_of_time_minutes": round(equation_minutes, 2),
        "total_correction_minutes": round(total_minutes, 2),
        "central_longitude": central_longitude,
        "location": location.to_dict(),
    }


def _location_from_dict(value: dict[str, Any]) -> BirthLocation:
    return BirthLocation(
        id=str(value.get("id") or ""),
        scope=str(value.get("scope") or ""),
        display_name=str(value.get("display_name") or ""),
        latitude=float(value.get("latitude")),
        longitude=float(value.get("longitude")),
        timezone=str(value.get("timezone") or "Asia/Shanghai"),
        country=str(value.get("country") or ""),
        province=str(value.get("province") or ""),
        city=str(value.get("city") or ""),
        district=str(value.get("district") or ""),
        region=str(value.get("region") or ""),
    )


def _timezone_central_longitude(value: datetime) -> float:
    if getattr(value.tzinfo, "key", "") == "Asia/Shanghai":
        return 120.0
    offset = value.utcoffset() or timedelta()
    return offset.total_seconds() / 3600 * 15


def _equation_of_time_minutes(value: datetime) -> float:
    day_of_year = int(value.strftime("%j"))
    angle = math.radians((360 / 365) * (day_of_year - 81))
    return 9.87 * math.sin(2 * angle) - 7.53 * math.cos(angle) - 1.5 * math.sin(angle)
