import json
import sys
import urllib.parse
import urllib.request
from typing import Optional, Tuple

# Geocoder setup (OpenStreetMap Nominatim). Replace contact@example.com with a real contact per policy.
USER_AGENT = "exampler-geocoder/1.0 (contact@example.com)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def _perform_query(q: str) -> Optional[Tuple[float, float, str]]:
    params = {"format": "json", "q": q, "limit": 1, "addressdetails": 0}
    url = NOMINATIM_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
            if not data:
                return None
            first = data[0]
            return float(first["lat"]), float(first["lon"]), first.get("display_name", "")
    except Exception as e:
        # Print debug info to stderr to help diagnose failures (network, rate-limits, bad UA)
        print(f"geocode: query failed for '{q}': {e}", file=sys.stderr)
        return None


def geocode(number: Optional[str], street: str, city: str, country: str) -> Optional[Tuple[float, float, str]]:
    """Return (lat, lon, display_name) for the provided address parts or None if not found.

    This function will try a few progressively simpler queries (full address -> without number -> city+country)
    and prints debug information to stderr when queries fail. That helps explain why address lookups may not
    resolve (network issues, rate limiting, or incomplete address parts).
    """
    street_part = " ".join(p.strip() for p in (number or "", street or "") if p and p.strip())
    parts = [p for p in (street_part, city, country) if p and p.strip()]

    # Build a list of candidate queries (most-specific first)
    candidates = []
    if parts:
        candidates.append(", ".join(parts))
    # without number
    if street and city and country:
        candidates.append(", ".join((street.strip(), city.strip(), country.strip())))
    # city + country
    if city and country:
        candidates.append(f"{city.strip()}, {country.strip()}")
    # fallback: street alone
    if street:
        candidates.append(street.strip())

    # Remove duplicates while preserving order
    seen = set()
    queries = []
    for c in candidates:
        if c and c not in seen:
            seen.add(c)
            queries.append(c)

    for q in queries:
        # Attempt the query
        result = _perform_query(q)
        if result is not None:
            return result

    # If nothing worked, print a concise debug line and return None
    if queries:
        print(f"geocode: no results for queries: {queries}", file=sys.stderr)
    else:
        print("geocode: no address parts provided", file=sys.stderr)
    return None
