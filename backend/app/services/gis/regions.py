"""Study-region registry and box geometry. Owner: Developer A (GIS tasks).

Every study region is a 0.1 degree IMERG cell centre. Boxes are k x k cells
around that centre, with edges on cell edges. Bounds order everywhere:
[south, north, west, east].
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from app.core.config import BOX_KM, BOX_SIZES, GRID_STEP, REGIONS_FILE, SPATIAL_SIDE
from app.core.errors import RegionNotFound


@dataclass(frozen=True)
class Region:
    id: str
    name: str
    admin_region: str
    centre_lat: float
    centre_lon: float
    coastal: bool
    verified: bool

    def bounds(self, side: int) -> list[float]:
        """[south, north, west, east] of a side x side cell box around the centre cell."""
        half = side * GRID_STEP / 2
        return [
            round(self.centre_lat - half, 2),
            round(self.centre_lat + half, 2),
            round(self.centre_lon - half, 2),
            round(self.centre_lon + half, 2),
        ]

    def box_bounds(self, box: str) -> list[float]:
        return self.bounds(BOX_SIZES[box])

    @property
    def grid_bounds(self) -> list[float]:
        """Extent of the exploratory trend map (9 x 9 cells)."""
        return self.bounds(SPATIAL_SIDE)

    def grid_cells(self) -> list[tuple[float, float]]:
        """Cell centres (lat, lon) of the 9 x 9 grid, south-west first."""
        south, _, west, _ = self.grid_bounds
        return [
            (round(south + GRID_STEP * (i + 0.5), 2), round(west + GRID_STEP * (j + 0.5), 2))
            for i in range(SPATIAL_SIDE)
            for j in range(SPATIAL_SIDE)
        ]

    def box_label(self, box: str) -> str:
        side = BOX_SIZES[box]
        return f"{self.name}, {side} x {side} cells (about {BOX_KM[box]} km)"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "admin_region": self.admin_region,
            "centre": [self.centre_lat, self.centre_lon],
            "coastal": self.coastal,
            "verified": self.verified,
            "boxes": {box: {"label": self.box_label(box), "bounds": self.box_bounds(box)} for box in BOX_SIZES},
            "grid_bounds": self.grid_bounds,
        }


@lru_cache
def load_regions(path: Path = REGIONS_FILE) -> dict[str, Region]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    regions = {}
    for r in raw["regions"]:
        regions[r["id"]] = Region(
            id=r["id"],
            name=r["name"],
            admin_region=r["admin_region"],
            centre_lat=float(r["centre_lat"]),
            centre_lon=float(r["centre_lon"]),
            coastal=bool(r["coastal"]),
            verified=bool(r.get("verified", False)),
        )
    return regions


def get_region(region_id: str) -> Region:
    regions = load_regions()
    if region_id not in regions:
        raise RegionNotFound(f"unknown region {region_id!r}; choose one of {', '.join(regions)}")
    return regions[region_id]
