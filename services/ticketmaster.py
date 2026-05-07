import os
import httpx

TM_BASE = "https://app.ticketmaster.com/discovery/v2"


def _api_key() -> str:
    key = os.getenv("TM_API_KEY")
    if not key:
        raise ValueError("TM_API_KEY not set")
    return key


def _clean_event(event: dict) -> dict:
    dates = event.get("dates", {}).get("start", {})
    date_str = dates.get("localDate", "TBD")
    time_str = dates.get("localTime", "")

    venues = event.get("_embedded", {}).get("venues", [])
    venue_name = venues[0].get("name", "TBD") if venues else "TBD"
    venue_city = venues[0].get("city", {}).get("name", "") if venues else ""

    price_ranges = event.get("priceRanges", [])
    if price_ranges:
        pr = price_ranges[0]
        price = f"${pr.get('min', '?')} – ${pr.get('max', '?')} {pr.get('currency', 'USD')}"
    else:
        price = "Price not listed"

    images = event.get("images", [])
    image_url = images[0].get("url", "") if images else ""

    return {
        "id": event.get("id"),
        "name": event.get("name"),
        "date": date_str,
        "time": time_str,
        "venue": venue_name,
        "city": venue_city,
        "price": price,
        "url": event.get("url", ""),
        "image": image_url,
    }


async def search_events(
    city: str | None = None,
    genre: str | None = None,
    keyword: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    size: int = 5,
) -> list[dict]:
    params: dict = {"apikey": _api_key(), "size": size}
    if city:
        params["city"] = city
    if genre:
        params["classificationName"] = genre
    if keyword:
        params["keyword"] = keyword
    if start_date:
        params["startDateTime"] = f"{start_date}T00:00:00Z"
    if end_date:
        params["endDateTime"] = f"{end_date}T23:59:59Z"

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TM_BASE}/events.json", params=params)
        resp.raise_for_status()
        data = resp.json()

    events = data.get("_embedded", {}).get("events", [])
    return [_clean_event(e) for e in events]


async def get_event(event_id: str) -> dict | None:
    params = {"apikey": _api_key()}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{TM_BASE}/events/{event_id}.json", params=params)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return _clean_event(resp.json())
