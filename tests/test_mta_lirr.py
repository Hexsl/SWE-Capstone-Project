"""LIRR importer tests on a tiny hand-made GTFS feed (no network, no real MongoDB)."""
import io
import zipfile

import mongomock
import pytest

from database import mta_lirr
from database import queries as q
from database.schemas import COLLECTIONS
from schema_check import errors

# Two branches. Shape "B-long" passes every Babylon station; "B-short" only some, so it adds
# nothing and should be dropped. Station 99 is in stops.txt but no trip stops there.
FEED = {
    "routes.txt": "route_id,route_long_name,route_type,route_color,route_text_color\n"
                  "1,Babylon Branch,2,00985F,FFFFFF\n"
                  "9,Port Washington Branch,2,c60c30,FFFFFF\n",
    "stops.txt": "stop_id,stop_code,stop_name,stop_lat,stop_lon,wheelchair_boarding\n"
                 "1,PEN,Penn Station,40.7506,-73.9935,1\n"
                 "2,JAM,Jamaica,40.6996,-73.8081,1\n"
                 "3,BTA,Babylon,40.7004,-73.3238,2\n"
                 "4,PWS,Port Washington,40.8297,-73.6869,1\n"
                 "99,XXX,Closed Station,40.8,-73.5,1\n",
    "trips.txt": "route_id,service_id,trip_id,direction_id,shape_id\n"
                 "1,S,t1,0,B-long\n"
                 "1,S,t2,0,B-short\n"
                 "9,S,t3,0,PW\n",
    "stop_times.txt": "trip_id,arrival_time,departure_time,stop_id,stop_sequence\n"
                      "t1,08:00:00,08:00:00,1,1\nt1,08:20:00,08:20:00,2,2\nt1,09:10:00,09:10:00,3,3\n"
                      "t2,08:00:00,08:00:00,2,1\nt2,08:50:00,08:50:00,3,2\n"
                      "t3,08:00:00,08:00:00,1,1\nt3,08:40:00,08:40:00,4,2\n",
    "shapes.txt": "shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence\n"
                  # B-long: listed out of order on purpose; the middle points sit on a straight line
                  "B-long,40.7004,-73.3238,4\nB-long,40.7506,-73.9935,1\n"
                  "B-long,40.72510,-73.90085,2\nB-long,40.6996,-73.8081,3\n"
                  "B-short,40.6996,-73.8081,1\nB-short,40.7004,-73.3238,2\n"
                  "PW,40.7506,-73.9935,1\nPW,40.8297,-73.6869,2\n",
}


def make_zip(files=FEED):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in files.items():
            zf.writestr(name, text)
    return zipfile.ZipFile(buf)


@pytest.fixture()
def db(monkeypatch):
    db = mongomock.MongoClient()["transithub_test"]

    def upsert(coll, key, docs):          # mongomock's bulk_write doesn't support newer PyMongo
        for doc in docs:
            coll.update_one({key: doc[key]}, {"$set": doc}, upsert=True)

    monkeypatch.setattr(mta_lirr, "_upsert", upsert)
    return db


def test_parse_stations():
    stops, _ = mta_lirr.parse_feed(make_zip())
    by_id = {s["stop_id"]: s for s in stops}
    assert sorted(by_id) == ["lirr-1", "lirr-2", "lirr-3", "lirr-4"]       # unserved station 99 skipped
    assert by_id["lirr-1"]["route_ids"] == ["lirr-1", "lirr-9"]           # Penn is on both branches
    assert by_id["lirr-1"]["location"]["coordinates"] == [-73.9935, 40.7506]  # GeoJSON: lon first
    assert by_id["lirr-3"]["wheelchair_accessible"] is False              # GTFS 2 = not accessible
    assert all(s["mode"] == "rail" and s["agency"] == "LIRR" for s in stops)


def test_parse_branches():
    _, routes = mta_lirr.parse_feed(make_zip())
    babylon, port_wash = routes
    assert babylon["route_id"] == "lirr-1" and babylon["short_name"] == "Babylon"
    assert port_wash["color"] == "#C60C30"
    # B-short covers no station B-long misses, so only one line is drawn;
    # its points come back in sequence order with the straight-line midpoint removed
    assert babylon["shape"] == {"type": "MultiLineString",
                                "coordinates": [[[-73.9935, 40.7506], [-73.8081, 40.6996], [-73.3238, 40.7004]]]}


def test_import_matches_validators_and_records_source(db):
    assert mta_lirr.import_lirr(db, make_zip()) == (4, 2)
    for name in ("stops", "routes", "data_sources"):
        for doc in db[name].find():
            assert errors(doc, COLLECTIONS[name]["validator"]["$jsonSchema"]) == []
    assert q.source_status(db, mta_lirr.SOURCE_KEY)["status"] == "ok"


def test_reimport_removes_stations_that_left_the_feed(db):
    db.stops.insert_one({"stop_id": "127", "name": "Times Sq - 42 St", "mode": "subway"})  # not LIRR: kept
    mta_lirr.import_lirr(db, make_zip())
    smaller = {**FEED, "trips.txt": "route_id,service_id,trip_id,direction_id,shape_id\n1,S,t1,0,B-long\n"}
    mta_lirr.import_lirr(db, make_zip(smaller))
    assert sorted(s["stop_id"] for s in db.stops.find()) == ["127", "lirr-1", "lirr-2", "lirr-3"]
    assert [r["route_id"] for r in db.routes.find()] == ["lirr-1", "lirr-9"]   # routes.txt still lists both


def test_failed_import_is_recorded(db):
    with pytest.raises(KeyError):
        mta_lirr.import_lirr(db, make_zip({k: v for k, v in FEED.items() if k != "trips.txt"}))
    assert q.source_status(db, mta_lirr.SOURCE_KEY)["status"] == "down"


def test_map_layer_only_returns_that_agency(db):
    db.stops.insert_one({"stop_id": "127", "name": "Times Sq - 42 St", "mode": "subway"})
    mta_lirr.import_lirr(db, make_zip())
    layer = q.map_layer(db, "LIRR")
    assert [s["name"] for s in layer["stops"]] == ["Babylon", "Jamaica", "Penn Station", "Port Washington"]
    assert "_id" not in layer["stops"][0] and len(layer["routes"]) == 2
