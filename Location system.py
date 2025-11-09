import json
import urllib.parse
import urllib.request
from typing import Optional, Tuple

# Replace contact@example.com with a real contact per Nominatim policy
USER_AGENT = "exampler-geocoder/1.0 (contact@example.com)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

def geocode(number: Optional[str], street: str, city: str, country: str) -> Optional[Tuple[float, float, str]]:
    street_part = " ".join(p.strip() for p in (number or "", street or "") if p and p.strip())
    parts = [p for p in (street_part, city, country) if p and p.strip()]
    if not parts:
        return None
    q = ", ".join(parts)
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
    except Exception:
        return None

def prompt_and_run() -> None:
    print("Enter location details (leave blank if unknown).")
    number = input("Address (number) : ").strip()
    street = input("Street name      : ").strip()
    city = input("City / Town      : ").strip()
    country = input("Country          : ").strip()

    result = geocode(number or None, street, city, country)
    if result is None:
        print("Location not found.")
    else:
        lat, lon, name = result
        print(f"Found: {name}")
        print(f"Latitude: {lat}")
        print(f"Longitude: {lon}")

if __name__ == "__main__":
    prompt_and_run()
