"""Create every collection with its validator and indexes. Safe to run more than once.

    python -m database.init_db           # create/update collections + indexes
    python -m database.init_db --seed    # same, then load sample data
    python -m database.init_db --reset   # DROP everything first (dev only!)
"""
import argparse

from pymongo.errors import CollectionInvalid

from .db import get_db
from .schemas import COLLECTIONS


def sync_indexes(coll, wanted) -> None:
    """Drop indexes that are no longer in schemas.py (or whose options changed), then create the rest."""
    wanted_by_name = {ix.document["name"]: ix.document for ix in wanted}
    for name, info in coll.index_information().items():
        if name == "_id_":
            continue
        want = wanted_by_name.get(name)
        changed = want and any(info.get(k) != want.get(k) for k in
                               ("unique", "expireAfterSeconds", "partialFilterExpression", "sparse"))
        if not want or changed:
            coll.drop_index(name)
            print(f"  dropped  {coll.name}.{name}")
    if wanted:
        coll.create_indexes(wanted)


def init_collections(db) -> None:
    existing = set(db.list_collection_names())
    for name, spec in COLLECTIONS.items():
        if name in existing:
            # Update the validator in place so schema changes apply to existing databases
            db.command("collMod", name, validator=spec["validator"], validationLevel="moderate")
            action = "updated"
        else:
            try:
                db.create_collection(name, validator=spec["validator"], validationLevel="moderate")
            except CollectionInvalid:
                pass  # created by a teammate at the same moment
            action = "created"
        sync_indexes(db[name], spec.get("indexes", []))
        print(f"  {action:8} {name:18} ({len(spec.get('indexes', []))} indexes)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--seed", action="store_true", help="load sample data after creating collections")
    parser.add_argument("--reset", action="store_true", help="drop all app collections first (destroys data)")
    args = parser.parse_args()

    db = get_db()
    print(f"Database: {db.name}")

    if args.reset:
        if input(f"Type the database name '{db.name}' to drop all its collections: ") != db.name:
            print("Aborted.")
            return
        for name in COLLECTIONS:
            db.drop_collection(name)
        print("  dropped all collections")

    init_collections(db)

    if args.seed:
        from .seed import seed

        seed(db)
    print("Done.")


if __name__ == "__main__":
    main()
