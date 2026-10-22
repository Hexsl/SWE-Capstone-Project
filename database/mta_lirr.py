"""Import Long Island Rail Road stations and branches from the MTA's static GTFS feed.

    python -m database.mta_lirr            # download the feed and upsert into stops + routes

Stations go into `stops` and branches into `routes`, both with mode "rail" and agency "LIRR".
LIRR ids are numbers that clash with subway ids ("1" is both a subway line and an LIRR branch),
so every id gets a "lirr-" prefix. Safe to run again: it upserts, and removes stations that
are no longer in the feed.
"""
import csv
import io
import ssl
import urllib.request
import zipfile
from collections import defaultdict

import certifi
from pymongo import UpdateOne

from . import queries

FEED_URL = "https://rrgtfsfeeds.s3.amazonaws.com/gtfslirr.zip"
SOURCE_KEY = "mta_lirr_gtfs"
# The schedule feed changes every few weeks, so it's only "stale" if the import hasn't run for a week
SOURCE_INFO = {"name": "MTA LIRR GTFS (stations and branches)", "stale_after_seconds": 7 * 24 * 3600}
AGENCY = "LIRR"
PREFIX = "lirr-"
SIMPLIFY_DEG = 0.0001     # ~10 m: how far a simplified branch line may stray from the real track


def _rows(zf: zipfile.ZipFile, name: str):
    with zf.open(name) as f:
        yield from csv.DictReader(io.TextIOWrapper(f, encoding="utf-8-sig"))


def _simplify(points, tolerance=SIMPLIFY_DEG):
    """Douglas-Peucker: keep only the points needed to stay within `tolerance` of the original line."""
    keep = [False] * len(points)
    keep[0] = keep[-1] = True
    stack = [(0, len(points) - 1)]
    while stack:
        a, b = stack.pop()
        (x1, y1), (x2, y2) = points[a], points[b]
        dx, dy = x2 - x1, y2 - y1
        length = (dx * dx + dy * dy) ** 0.5
        far, far_i = 0.0, None
        for i in range(a + 1, b):
            x, y = points[i]
            d = abs(dy * (x - x1) - dx * (y - y1)) / length if length else ((x - x1) ** 2 + (y - y1) ** 2) ** 0.5
            if d > far:
                far, far_i = d, i
        if far_i is not None and far > tolerance:
            keep[far_i] = True
            stack += [(a, far_i), (far_i, b)]
    return [[round(x, 5), round(y, 5)] for (x, y), k in zip(points, keep) if k]


def parse_feed(zf: zipfile.ZipFile):
    """Turn a GTFS zip into (stops, routes) documents ready for MongoDB."""
    trip_route, trip_shape = {}, {}
    for t in _rows(zf, "trips.txt"):
        trip_route[t["trip_id"]] = t["route_id"]
        trip_shape[t["trip_id"]] = t.get("shape_id") or None

    routes_at_stop = defaultdict(set)
    stops_on_shape = defaultdict(set)
    for st in _rows(zf, "stop_times.txt"):
        trip = st["trip_id"]
        if trip not in trip_route:
            continue  # stop time for a trip that isn't in trips.txt
        routes_at_stop[st["stop_id"]].add(trip_route[trip])
        if trip_shape[trip]:
            stops_on_shape[trip_shape[trip]].add(st["stop_id"])

    shape_points = defaultdict(list)
    for p in _rows(zf, "shapes.txt"):
        shape_points[p["shape_id"]].append((int(p["shape_pt_sequence"]), float(p["shape_pt_lon"]), float(p["shape_pt_lat"])))

    shapes_of_route = defaultdict(set)
    for trip, shape in trip_shape.items():
        if shape in shape_points:
            shapes_of_route[trip_route[trip]].add(shape)

    stops = []
    for s in _rows(zf, "stops.txt"):
        if s["stop_id"] not in routes_at_stop:
            continue  # not served by any trip
        stops.append({
            "stop_id": PREFIX + s["stop_id"], "name": s["stop_name"], "mode": "rail", "agency": AGENCY,
            "location": {"type": "Point", "coordinates": [float(s["stop_lon"]), float(s["stop_lat"])]},
            "route_ids": sorted((PREFIX + r for r in routes_at_stop[s["stop_id"]]), key=_route_order),
            "wheelchair_accessible": s.get("wheelchair_boarding") == "1",
        })

    routes = []
    for r in _rows(zf, "routes.txt"):
        doc = {
            "route_id": PREFIX + r["route_id"], "short_name": r["route_long_name"].replace(" Branch", ""),
            "long_name": r["route_long_name"], "mode": "rail", "agency": AGENCY,
            "color": "#" + (r.get("route_color") or "4D5357").upper(),
            "text_color": "#" + (r.get("route_text_color") or "FFFFFF").upper(),
        }
        lines = [_simplify([(lon, lat) for _, lon, lat in sorted(shape_points[sid])])
                 for sid in _covering_shapes(shapes_of_route[r["route_id"]], shape_points, stops_on_shape)]
        if lines:
            doc["shape"] = {"type": "MultiLineString", "coordinates": lines}
        routes.append(doc)
    routes.sort(key=lambda d: _route_order(d["route_id"]))
    return stops, routes


def _route_order(route_id):
    return int(route_id[len(PREFIX):]) if route_id[len(PREFIX):].isdigit() else 999


def _covering_shapes(shape_ids, shape_points, stops_on_shape):
    """Fewest shapes that together pass every station on the branch: longest first, then fill the gaps.

    A branch has dozens of shapes (one per stopping pattern and direction); drawing them all
    would send megabytes to the phone for lines that sit on top of each other.
    """
    remaining = sorted(shape_ids, key=lambda sid: -len(shape_points[sid]))
    covered, chosen = set(), []
    for sid in remaining:
        if not chosen or not stops_on_shape[sid] <= covered:
            chosen.append(sid)
            covered |= stops_on_shape[sid]
    return chosen


def _upsert(coll, key, docs):
    ops = [UpdateOne({key: d[key]}, {"$set": d}, upsert=True) for d in docs]
    if ops:
        coll.bulk_write(ops)


def import_lirr(db, zf: zipfile.ZipFile):
    """Upsert LIRR stations and branches, drop stations that left the feed, and record feed health."""
    try:
        stops, routes = parse_feed(zf)
        fresh = {"source": SOURCE_KEY, "updated_at": queries.now()}
        _upsert(db.stops, "stop_id", [{**s, **fresh} for s in stops])
        _upsert(db.routes, "route_id", [{**r, **fresh} for r in routes])
        db.stops.delete_many({"agency": AGENCY, "stop_id": {"$nin": [s["stop_id"] for s in stops]}})
        db.routes.delete_many({"agency": AGENCY, "route_id": {"$nin": [r["route_id"] for r in routes]}})
    except Exception as exc:
        queries.record_source_result(db, SOURCE_KEY, ok=False, error=exc, **SOURCE_INFO)
        raise
    queries.record_source_result(db, SOURCE_KEY, ok=True, **SOURCE_INFO)
    return len(stops), len(routes)


def download(url=FEED_URL) -> zipfile.ZipFile:
    ctx = ssl.create_default_context(cafile=certifi.where())   # see db.py: python.org macOS Python has no CA certs
    with urllib.request.urlopen(url, timeout=60, context=ctx) as resp:
        return zipfile.ZipFile(io.BytesIO(resp.read()))


def main() -> None:
    from .db import get_db

    n_stops, n_routes = import_lirr(get_db(), download())
    print(f"  imported {n_stops} LIRR stations and {n_routes} branches")


if __name__ == "__main__":
    main()
