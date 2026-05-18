import logging
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse
import xml.etree.ElementTree as ET
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import get_settings

log = logging.getLogger(__name__)

TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
DUCKDUCKGO_HTML_URL = "https://duckduckgo.com/html/"
BING_RSS_URL = "https://www.bing.com/search"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

BLOCKED_ORGANIC_DOMAINS = (
    "google.",
    "bing.",
    "duckduckgo.",
    "yahoo.",
    "youtube.",
    "wikipedia.",
    "linkedin.",
    "tripadvisor.",
    "yelp.",
    "yellowpages.",
    "justdial.",
    "mapcarta.",
    "foursquare.",
    "booksy.",
    "chamberofcommerce.",
    "cybo.",
    "nepalyp.",
    "worldwidephonebooks.",
    "beautynailhairsalons.",
    "therighthairstyles.",
    "find-open.",
    "near-me.",
    "nicelocal.",
    "threebestrated.",
)


def clean_duckduckgo_url(url: str) -> str:
    parsed = urlparse(url)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return unquote(target)
    return url


def is_usable_business_url(url: str) -> bool:
    parsed = urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.")
    return bool(host) and not any(domain in host for domain in BLOCKED_ORGANIC_DOMAINS)


class DuckDuckGoResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._active_link: dict[str, str] | None = None
        self._capture_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        classes = attr.get("class", "")
        if tag == "a" and "result__a" in classes:
            self._active_link = {"url": clean_duckduckgo_url(attr.get("href") or ""), "title": ""}
            self._capture_title = True

    def handle_data(self, data: str) -> None:
        if self._capture_title and self._active_link is not None:
            self._active_link["title"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_title and self._active_link is not None:
            title = " ".join(self._active_link["title"].split())
            url = self._active_link["url"]
            if title and is_usable_business_url(url):
                self.results.append({"title": title, "url": url})
            self._active_link = None
            self._capture_title = False


def organic_place_id(url: str) -> str:
    parsed = urlparse(url)
    return f"organic:{parsed.netloc.lower()}{parsed.path}".rstrip("/")


def location_from_query(query: str) -> str:
    if " in " in query:
        return query.rsplit(" in ", 1)[1]
    return query


def osm_tags_for_query(query: str) -> list[tuple[str, str]]:
    lowered = query.lower()
    mappings = [
        (("dentist", "dental"), [("amenity", "dentist")]),
        (("salon", "saloon", "hair", "barber"), [("shop", "hairdresser")]),
        (("restaurant",), [("amenity", "restaurant")]),
        (("cafe", "coffee"), [("amenity", "cafe")]),
        (("hotel",), [("tourism", "hotel")]),
        (("gym", "fitness"), [("leisure", "fitness_centre")]),
        (("spa",), [("leisure", "spa"), ("shop", "beauty")]),
        (("pharmacy",), [("amenity", "pharmacy")]),
        (("clinic",), [("amenity", "clinic")]),
        (("lawyer", "legal"), [("office", "lawyer")]),
        (("repair",), [("shop", "repair")]),
        (("plumber",), [("craft", "plumber")]),
        (("electrician",), [("craft", "electrician")]),
    ]
    tags: list[tuple[str, str]] = []
    for needles, mapped in mappings:
        if any(needle in lowered for needle in needles):
            tags.extend(mapped)
    return tags


def osm_address(tags_data: dict[str, str]) -> str | None:
    parts = [
        " ".join(part for part in [tags_data.get("addr:housenumber"), tags_data.get("addr:street")] if part),
        tags_data.get("addr:city"),
        tags_data.get("addr:state"),
        tags_data.get("addr:postcode"),
        tags_data.get("addr:country"),
    ]
    address = ", ".join(part for part in parts if part)
    return address or None


def osm_url(element: dict[str, Any]) -> str:
    return f"https://www.openstreetmap.org/{element.get('type')}/{element.get('id')}"


class GooglePlacesClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=20), retry=retry_if_exception_type(httpx.HTTPError))
    async def search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        if not self.settings.google_places_api_key:
            log.info("GOOGLE_PLACES_API_KEY missing; using organic web search for %s", query)
            map_results = await self.openstreetmap_search(query, max_results)
            organic_results = await self.organic_search(query, max_results)
            return (map_results + organic_results)[:max_results]
        params = {"query": query, "key": self.settings.google_places_api_key}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(TEXT_SEARCH_URL, params=params)
            response.raise_for_status()
        data = response.json()
        if data.get("status") not in {"OK", "ZERO_RESULTS"}:
            raise RuntimeError(f"Google Places search failed: {data.get('status')} {data.get('error_message')}")
        return data.get("results", [])[:max_results]

    async def openstreetmap_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        tags = osm_tags_for_query(query)
        if not tags:
            return []
        async with httpx.AsyncClient(timeout=25, headers={"User-Agent": "LeadHunter/1.0"}) as client:
            geo = await client.get(NOMINATIM_URL, params={"q": location_from_query(query), "format": "json", "limit": 1})
            geo.raise_for_status()
            geocoded = geo.json()
            if not geocoded:
                return []
            lat = float(geocoded[0]["lat"])
            lon = float(geocoded[0]["lon"])
            clauses = "\n".join(
                f'node(around:12000,{lat},{lon})["{key}"="{value}"];'
                f'way(around:12000,{lat},{lon})["{key}"="{value}"];'
                f'relation(around:12000,{lat},{lon})["{key}"="{value}"];'
                for key, value in tags
            )
            overpass_query = f"""
            [out:json][timeout:25];
            (
              {clauses}
            );
            out center tags {max_results};
            """
            response = await client.post(OVERPASS_URL, data={"data": overpass_query})
            response.raise_for_status()
        elements = response.json().get("elements", [])
        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        for element in elements:
            tags_data = element.get("tags") or {}
            name = tags_data.get("name")
            if not name:
                continue
            osm_id = f"osm:{element.get('type')}:{element.get('id')}"
            if osm_id in seen:
                continue
            seen.add(osm_id)
            phone = tags_data.get("phone") or tags_data.get("contact:phone")
            website = tags_data.get("website") or tags_data.get("contact:website")
            center = element.get("center") or element
            category = tags_data.get("amenity") or tags_data.get("shop") or tags_data.get("craft") or "local business"
            results.append({
                "source": "openstreetmap",
                "place_id": osm_id,
                "name": name,
                "category": category,
                "address": osm_address(tags_data),
                "phone": phone,
                "website": website,
                "url": osm_url(element),
                "types": [category],
                "business_status": "OPERATIONAL",
                "geometry": {"location": {"lat": center.get("lat"), "lng": center.get("lon")}},
                "raw_tags": tags_data,
            })
            if len(results) >= max_results:
                break
        return results

    async def organic_search(self, query: str, max_results: int) -> list[dict[str, Any]]:
        search_query = f'{query} business contact website'
        results = await self.duckduckgo_search(search_query, query, max_results)
        if results:
            return results
        return await self.bing_rss_search(search_query, query, max_results)

    async def duckduckgo_search(self, search_query: str, query: str, max_results: int) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
            try:
                response = await client.get(DUCKDUCKGO_HTML_URL, params={"q": search_query})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                log.warning("DuckDuckGo organic search failed for %s: %s", search_query, exc.response.status_code)
                return []
        parser = DuckDuckGoResultParser()
        parser.feed(response.text)
        return self.to_organic_results(parser.results, query, max_results)

    async def bing_rss_search(self, search_query: str, query: str, max_results: int) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(timeout=20, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as client:
            try:
                response = await client.get(BING_RSS_URL, params={"format": "rss", "q": search_query})
                response.raise_for_status()
            except httpx.HTTPStatusError as exc:
                log.warning("Bing organic search failed for %s: %s", search_query, exc.response.status_code)
                return []
        try:
            root = ET.fromstring(response.text)
        except ET.ParseError:
            return []
        parsed: list[dict[str, str]] = []
        for item in root.findall("./channel/item"):
            title = " ".join((item.findtext("title") or "").split())
            url = item.findtext("link") or ""
            if title and is_usable_business_url(url):
                parsed.append({"title": title, "url": url})
        return self.to_organic_results(parsed, query, max_results)

    def to_organic_results(self, parsed: list[dict[str, str]], query: str, max_results: int) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        seen: set[str] = set()
        for item in parsed:
            url = item["url"]
            key = organic_place_id(url)
            if key in seen:
                continue
            seen.add(key)
            results.append({
                "source": "organic_web",
                "place_id": key,
                "name": item["title"],
                "website": url,
                "url": url,
                "types": [query],
                "business_status": "OPERATIONAL",
            })
            if len(results) >= max_results:
                break
        return results

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=20), retry=retry_if_exception_type(httpx.HTTPError))
    async def details(self, place_id: str) -> dict[str, Any] | None:
        if not self.settings.google_places_api_key:
            return None
        fields = ",".join([
            "place_id",
            "name",
            "formatted_address",
            "formatted_phone_number",
            "international_phone_number",
            "website",
            "url",
            "rating",
            "user_ratings_total",
            "business_status",
            "geometry",
            "types",
        ])
        params = {"place_id": place_id, "fields": fields, "key": self.settings.google_places_api_key}
        async with httpx.AsyncClient(timeout=20) as client:
            response = await client.get(DETAILS_URL, params=params)
            response.raise_for_status()
        data = response.json()
        if data.get("status") != "OK":
            log.warning("Place details failed for %s: %s", place_id, data.get("status"))
            return None
        return data.get("result")
