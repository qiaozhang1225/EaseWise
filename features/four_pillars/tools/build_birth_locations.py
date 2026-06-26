from __future__ import annotations

import json
import re
import shutil
import subprocess
import tarfile
import tempfile
import urllib.request
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
OUTPUT_PATH = ROOT / "features" / "four_pillars" / "knowledge" / "structured" / "birth-locations.json"
ALIYUN_GEO_URL = "https://geo.datav.aliyun.com/areas_v3/bound/{code}_full.json"
WORLD_CITIES_TARBALL = "https://registry.npmjs.org/world-cities-json/-/world-cities-json-1.0.1.tgz"
TZ_LOOKUP_TARBALL = "https://registry.npmjs.org/tz-lookup/-/tz-lookup-6.1.25.tgz"
CHINA_DIVISION_TARBALL = "https://registry.npmjs.org/province-city-china/-/province-city-china-8.5.8.tgz"

COMMON_OVERSEAS_COUNTRIES = {
    "US": "美国",
    "CA": "加拿大",
    "GB": "英国",
    "IE": "爱尔兰",
    "FR": "法国",
    "DE": "德国",
    "IT": "意大利",
    "ES": "西班牙",
    "PT": "葡萄牙",
    "NL": "荷兰",
    "BE": "比利时",
    "CH": "瑞士",
    "AT": "奥地利",
    "SE": "瑞典",
    "NO": "挪威",
    "DK": "丹麦",
    "FI": "芬兰",
    "PL": "波兰",
    "CZ": "捷克",
    "HU": "匈牙利",
    "GR": "希腊",
    "TR": "土耳其",
    "RU": "俄罗斯",
    "UA": "乌克兰",
    "AU": "澳大利亚",
    "NZ": "新西兰",
    "SG": "新加坡",
    "MY": "马来西亚",
    "TH": "泰国",
    "VN": "越南",
    "ID": "印度尼西亚",
    "PH": "菲律宾",
    "JP": "日本",
    "KR": "韩国",
    "IN": "印度",
    "AE": "阿联酋",
    "SA": "沙特阿拉伯",
    "IL": "以色列",
    "BR": "巴西",
    "MX": "墨西哥",
    "AR": "阿根廷",
    "CL": "智利",
    "PE": "秘鲁",
    "ZA": "南非",
    "EG": "埃及",
    "NG": "尼日利亚",
    "KE": "肯尼亚",
}


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="easewise-birth-locations-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        domestic_locations = build_domestic_locations(tmp_path)
        overseas_locations = build_overseas_locations(tmp_path)
    locations = domestic_locations + overseas_locations
    payload = {
        "metadata": {
            "generated_by": "features/four_pillars/tools/build_birth_locations.py",
            "domestic_source": "Aliyun DataV GeoAtlas areas_v3 bound *_full.json",
            "overseas_source": "world-cities-json 1.0.1, sourced from SimpleMaps World Cities Database",
            "timezone_source": "tz-lookup 6.1.25",
            "domestic_coverage": "China province/city/district levels from source GeoAtlas files",
            "overseas_policy": "Common overseas countries; capitals and cities with population >= 200000, capped at 120 per country after population sort.",
            "counts": {
                "domestic": len(domestic_locations),
                "overseas": len(overseas_locations),
                "total": len(locations),
            },
        },
        "default_location_id": "cn-110101",
        "locations": locations,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    print(payload["metadata"]["counts"])


def build_domestic_locations(tmp_path: Path) -> list[dict[str, Any]]:
    china_level_path = download_and_extract_json(CHINA_DIVISION_TARBALL, "package/dist/level.json", tmp_path / "province-city-china")
    china_level = json.loads(china_level_path.read_text(encoding="utf-8"))
    coordinate_lookup = build_domestic_coordinate_lookup(tmp_path)
    locations: list[dict[str, Any]] = []
    for province in china_level:
        province_code = str(province.get("code") or "")
        province_name = normalize_domestic_name(str(province.get("name") or ""))
        children = province.get("children") if isinstance(province.get("children"), list) else []
        if not children:
            locations.append(domestic_item_from_division(province_code, province_name, province_name, province_name, coordinate_lookup))
            continue
        for city in children:
            city_code = str(city.get("code") or "")
            city_name = normalize_domestic_name(str(city.get("name") or province_name))
            districts = city.get("children") if isinstance(city.get("children"), list) else []
            if not districts:
                district_name = city_name if city_code[:2] not in {"11", "12", "31", "50", "71", "81", "82"} else city_name
                locations.append(domestic_item_from_division(city_code, province_name, province_name if is_direct_admin(province_code) else city_name, district_name, coordinate_lookup))
                continue
            for district in districts:
                district_code = str(district.get("code") or "")
                district_name = normalize_domestic_name(str(district.get("name") or ""))
                locations.append(domestic_item_from_division(district_code, province_name, province_name if is_direct_admin(province_code) else city_name, district_name, coordinate_lookup))
    return apply_domestic_sibling_coordinate_fallback(dedupe_locations(locations))


def build_domestic_coordinate_lookup(tmp_path: Path) -> dict[str, dict[str, Any]]:
    lookup: dict[str, dict[str, Any]] = {}
    if OUTPUT_PATH.exists():
        try:
            existing = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
            for item in existing.get("locations", []):
                if item.get("scope") == "domestic":
                    code = str(item.get("adcode") or item.get("id", "").removeprefix("cn-"))
                    if code:
                        lookup[code] = {
                            "latitude": float(item["latitude"]),
                            "longitude": float(item["longitude"]),
                            "coordinate_source": item.get("coordinate_source") or "previous-birth-locations",
                        }
        except Exception:
            pass
    try:
        national = fetch_geojson(100000, tmp_path)
    except Exception:
        national = {"features": []}
    for feature in national.get("features", []):
        props = feature.get("properties") or {}
        add_coordinate(lookup, props, "aliyun-datav-center")
        try:
            province_code = int(props["adcode"])
        except Exception:
            continue
        try:
            province_geo = fetch_geojson(province_code, tmp_path)
        except Exception:
            continue
        for province_feature in province_geo.get("features", []):
            add_coordinate(lookup, province_feature.get("properties") or {}, "aliyun-datav-center")
    return lookup


def add_coordinate(lookup: dict[str, dict[str, Any]], props: dict[str, Any], source: str) -> None:
    code = str(props.get("adcode") or "")
    center = props.get("center") or props.get("centroid")
    if not code or not isinstance(center, list) or len(center) < 2:
        return
    lookup[code] = {
        "latitude": round(float(center[1]), 6),
        "longitude": round(float(center[0]), 6),
        "coordinate_source": source,
    }


def domestic_item_from_division(
    adcode: str,
    province: str,
    city: str,
    district: str,
    coordinate_lookup: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    coordinate, coordinate_source = resolve_domestic_coordinate(adcode, coordinate_lookup)
    return {
        "id": f"cn-{adcode}",
        "scope": "domestic",
        "country": "中国",
        "province": province,
        "city": city,
        "district": district,
        "region": "",
        "display_name": f"中国 {province} {city} {district}",
        "latitude": coordinate["latitude"],
        "longitude": coordinate["longitude"],
        "timezone": "Asia/Shanghai",
        "adcode": adcode,
        "source": "province-city-china",
        "coordinate_source": coordinate_source,
    }


def resolve_domestic_coordinate(adcode: str, lookup: dict[str, dict[str, Any]]) -> tuple[dict[str, float], str]:
    for code, source_name in [
        (adcode, "district-center"),
        (f"{adcode[:4]}00", "city-center-fallback"),
        (f"{adcode[:2]}0000", "province-center-fallback"),
    ]:
        if code in lookup:
            coordinate = lookup[code]
            return {
                "latitude": round(float(coordinate["latitude"]), 6),
                "longitude": round(float(coordinate["longitude"]), 6),
            }, str(coordinate.get("coordinate_source") or source_name)
    return {"latitude": 39.904989, "longitude": 116.405285}, "default-beijing-fallback"


def apply_domestic_sibling_coordinate_fallback(locations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    city_points: dict[tuple[str, str], list[tuple[float, float]]] = {}
    province_points: dict[str, list[tuple[float, float]]] = {}
    for item in locations:
        if item.get("coordinate_source") == "default-beijing-fallback":
            continue
        point = (float(item["latitude"]), float(item["longitude"]))
        city_points.setdefault((str(item.get("province") or ""), str(item.get("city") or "")), []).append(point)
        province_points.setdefault(str(item.get("province") or ""), []).append(point)
    for item in locations:
        if item.get("coordinate_source") != "default-beijing-fallback":
            continue
        points = city_points.get((str(item.get("province") or ""), str(item.get("city") or ""))) or province_points.get(str(item.get("province") or "")) or []
        if not points:
            continue
        item["latitude"] = round(sum(point[0] for point in points) / len(points), 6)
        item["longitude"] = round(sum(point[1] for point in points) / len(points), 6)
        item["coordinate_source"] = "sibling-average-fallback"
    return locations


def is_direct_admin(province_code: str) -> bool:
    return province_code[:2] in {"11", "12", "31", "50", "71", "81", "82"}


def build_overseas_locations(tmp_path: Path) -> list[dict[str, Any]]:
    world_cities_path = download_and_extract_json(WORLD_CITIES_TARBALL, "package/data/cities.json", tmp_path / "world-cities")
    tz_package_dir = download_and_extract_package(TZ_LOOKUP_TARBALL, tmp_path / "tz-lookup")
    cities = json.loads(world_cities_path.read_text(encoding="utf-8"))
    selected: list[dict[str, Any]] = []
    by_country: dict[str, list[dict[str, Any]]] = {}
    for city in cities:
        iso2 = str(city.get("iso2") or "").upper()
        if iso2 not in COMMON_OVERSEAS_COUNTRIES:
            continue
        population = parse_int(city.get("population"))
        if population < 200_000 and str(city.get("capital") or "") not in {"primary", "admin"}:
            continue
        by_country.setdefault(iso2, []).append(city)
    for iso2, items in by_country.items():
        items.sort(key=lambda item: (str(item.get("capital") or "") != "primary", -parse_int(item.get("population"))))
        selected.extend(items[:120])
    timezones = lookup_timezones(selected, tz_package_dir)
    locations = []
    if len(selected) != len(timezones):
        raise RuntimeError("timezone lookup count mismatch")
    for city, timezone_name in zip(selected, timezones):
        iso2 = str(city.get("iso2") or "").upper()
        city_name = str(city.get("city") or city.get("city_ascii") or "").strip()
        region_name = str(city.get("admin_name") or "").strip()
        country_name = COMMON_OVERSEAS_COUNTRIES.get(iso2) or str(city.get("country") or "").strip()
        latitude = round(float(city["lat"]), 6)
        longitude = round(float(city["lng"]), 6)
        city_id = slugify(f"{iso2}-{city.get('id') or city_name}")
        locations.append({
            "id": f"overseas-{city_id}",
            "scope": "overseas",
            "country": country_name,
            "province": "",
            "city": city_name,
            "district": "",
            "region": region_name,
            "display_name": " ".join(part for part in [country_name, region_name, city_name] if part),
            "latitude": latitude,
            "longitude": longitude,
            "timezone": timezone_name or fallback_timezone(iso2, longitude),
            "source": "world-cities-json",
            "coordinate_source": "world-cities-json",
        })
    return dedupe_locations(locations)


def fetch_geojson(code: int, tmp_path: Path) -> dict[str, Any]:
    target = tmp_path / f"{code}_full.json"
    if not target.exists():
        with urllib.request.urlopen(ALIYUN_GEO_URL.format(code=code), timeout=30) as response:
            target.write_bytes(response.read())
    return json.loads(target.read_text(encoding="utf-8"))


def domestic_item(props: dict[str, Any], province: str, city: str, district: str) -> dict[str, Any]:
    center = props.get("center") or props.get("centroid") or [116.405285, 39.904989]
    adcode = str(props["adcode"])
    return {
        "id": f"cn-{adcode}",
        "scope": "domestic",
        "country": "中国",
        "province": province,
        "city": city,
        "district": district,
        "region": "",
        "display_name": f"中国 {province} {city} {district}",
        "latitude": round(float(center[1]), 6),
        "longitude": round(float(center[0]), 6),
        "timezone": "Asia/Shanghai",
        "adcode": adcode,
        "source": "aliyun-datav-geoatlas",
        "coordinate_source": "aliyun-datav-center",
    }


def download_and_extract_json(tarball_url: str, member_name: str, target_dir: Path) -> Path:
    package_dir = download_and_extract_package(tarball_url, target_dir)
    return package_dir / member_name


def download_and_extract_package(tarball_url: str, target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    tarball_path = target_dir / "package.tgz"
    with urllib.request.urlopen(tarball_url, timeout=60) as response:
        tarball_path.write_bytes(response.read())
    with tarfile.open(tarball_path, "r:gz") as archive:
        archive.extractall(target_dir)
    return target_dir


def lookup_timezones(cities: list[dict[str, Any]], tz_package_dir: Path) -> list[str]:
    node = shutil.which("node")
    if not node:
        return [fallback_timezone(str(city.get("iso2") or ""), float(city.get("lng") or 0)) for city in cities]
    payload_path = tz_package_dir / "cities-for-timezone.json"
    output_path = tz_package_dir / "timezones.json"
    script_path = tz_package_dir / "lookup-timezones.cjs"
    payload_path.write_text(json.dumps([{"lat": city["lat"], "lng": city["lng"]} for city in cities]), encoding="utf-8")
    script_path.write_text(
        """
const fs = require('fs');
const tzlookup = require('./package/tz.js');
const input = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const output = input.map((item) => tzlookup(Number(item.lat), Number(item.lng)));
fs.writeFileSync(process.argv[3], JSON.stringify(output));
""".strip(),
        encoding="utf-8",
    )
    subprocess.run([node, str(script_path), str(payload_path), str(output_path)], check=True)
    return json.loads(output_path.read_text(encoding="utf-8"))


def fallback_timezone(iso2: str, longitude: float) -> str:
    mapping = {
        "US": "America/New_York",
        "CA": "America/Toronto",
        "GB": "Europe/London",
        "AU": "Australia/Sydney",
        "JP": "Asia/Tokyo",
        "KR": "Asia/Seoul",
        "SG": "Asia/Singapore",
        "MY": "Asia/Kuala_Lumpur",
        "TH": "Asia/Bangkok",
        "IN": "Asia/Kolkata",
        "AE": "Asia/Dubai",
        "NZ": "Pacific/Auckland",
    }
    if iso2 in mapping:
        return mapping[iso2]
    offset = round(longitude / 15)
    sign = "-" if offset >= 0 else "+"
    return f"Etc/GMT{sign}{abs(offset)}"


def parse_int(value: Any) -> int:
    try:
        return int(float(value or 0))
    except Exception:
        return 0


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_domestic_name(value: str) -> str:
    return value.strip()


def dedupe_locations(locations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result = []
    for item in locations:
        location_id = str(item.get("id") or "")
        if not location_id or location_id in seen:
            continue
        seen.add(location_id)
        result.append(item)
    return result


if __name__ == "__main__":
    main()
