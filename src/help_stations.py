import json
import os
from typing import List, Optional


class HelpStation:
    def __init__(self, persistence_file: str = 'data/stations.json'):
        """Manage help stations with JSON persistence."""
        self.stations: List[str] = []
        # optional mapping of station name -> (x, y) coordinates
        self._locations = {}
        self._persistence_file = persistence_file
        # Ensure directory exists
        dirpath = os.path.dirname(self._persistence_file)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        self._load()

    def _load(self):
        try:
            if os.path.exists(self._persistence_file):
                with open(self._persistence_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        if 'stations' in data:
                            self.stations = [s for s in data['stations'] if isinstance(s, str)]
                        if 'locations' in data and isinstance(data['locations'], dict):
                            # load locations, ensure tuples
                            for k, v in data['locations'].items():
                                if isinstance(v, list) and len(v) == 2:
                                    self._locations[k] = tuple(v)
        except Exception:
            self.stations = []
            self._locations = {}

    def _save(self):
        try:
            payload = {'stations': self.stations, 'locations': {k: list(v) for k, v in self._locations.items()}}
            with open(self._persistence_file, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
        except Exception:
            pass

    def add_station(self, name: str, location=None) -> bool:
        """Add a station by name. Location parameter is accepted for backward compatibility but ignored.
        Returns True if added, False if name already exists."""
        if not name:
            return False
        if name in self.stations:
            # If station already exists but a location is provided, update it.
            if location and isinstance(location, (list, tuple)) and len(location) == 2:
                try:
                    self._locations[name] = (float(location[0]), float(location[1]))
                    self._save()
                except Exception:
                    pass
            return False

        self.stations.append(name)
        if location and isinstance(location, (list, tuple)) and len(location) == 2:
            try:
                self._locations[name] = (float(location[0]), float(location[1]))
            except Exception:
                # ignore bad location format
                pass
        self._save()
        return True
        return True

    def delete_station(self, name: str) -> bool:
        """Delete a station by name. Returns True if deleted, False if not found."""
        if name not in self.stations:
            return False
        self.stations.remove(name)
        self._save()
        return True

    def get_station(self, name: str) -> Optional[str]:
        """Get a station by name."""
        return name if name in self.stations else None

    def calculate_distance(self, point, station_name: str) -> float:
        """Calculate Euclidean distance between a point (x,y) and a named station.
        Raises ValueError if station not found or station has no coordinates."""
        if station_name not in self.stations:
            raise ValueError("Station not found")
        if station_name not in self._locations:
            raise ValueError("Station has no coordinates")
        sx, sy = self._locations[station_name]
        try:
            px, py = float(point[0]), float(point[1])
        except Exception:
            raise ValueError("Invalid point")
        return ((sx - px) ** 2 + (sy - py) ** 2) ** 0.5

    def list_stations(self) -> List[str]:
        """Get a list of all station names."""
        return list(self.stations)