"""Document store. Uses MongoDB when MONGO_URI is set and reachable, otherwise JSON files
(so the app runs with zero setup). Same tiny interface either way."""
import json, os, threading
from pathlib import Path
from .. import config


class JsonStore:
    kind = "json"

    def __init__(self, root: Path):
        self.root, self.lock = root, threading.Lock()

    def _p(self, col, id_):
        d = self.root / col; d.mkdir(parents=True, exist_ok=True)
        return d / f"{id_}.json"

    def put(self, col, doc):
        p = self._p(col, doc["_id"]); tmp = p.with_suffix(".tmp")
        with self.lock:
            tmp.write_text(json.dumps(doc)); os.replace(tmp, p)

    def get(self, col, id_):
        p = self._p(col, id_)
        return json.loads(p.read_text()) if p.exists() else None

    def update(self, col, id_, fields):
        with self.lock:
            doc = self.get(col, id_)
            if doc is None: return None
            doc.update(fields)
            p = self._p(col, id_); tmp = p.with_suffix(".tmp")
            tmp.write_text(json.dumps(doc)); os.replace(tmp, p)
            return doc

    def list(self, col, **flt):
        d = self.root / col
        docs = [json.loads(f.read_text()) for f in d.glob("*.json")] if d.exists() else []
        return [x for x in docs if all(x.get(k) == v for k, v in flt.items())]

    def delete(self, col, id_):
        p = self._p(col, id_)
        if p.exists(): p.unlink()


class MongoStore:
    kind = "mongodb"

    def __init__(self, uri, db):
        from pymongo import MongoClient
        self.client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        self.client.admin.command("ping")
        self.db = self.client[db]

    def put(self, col, doc): self.db[col].replace_one({"_id": doc["_id"]}, doc, upsert=True)
    def get(self, col, id_): return self.db[col].find_one({"_id": id_})
    def update(self, col, id_, fields):
        return self.db[col].find_one_and_update({"_id": id_}, {"$set": fields}, return_document=True)
    def list(self, col, **flt): return list(self.db[col].find(flt))
    def delete(self, col, id_): self.db[col].delete_one({"_id": id_})


def _make():
    if config.MONGO_URI:
        try:
            return MongoStore(config.MONGO_URI, config.MONGO_DB)
        except Exception as e:
            print(f"[store] MongoDB unavailable ({e}); falling back to JSON files")
    return JsonStore(config.DB_DIR)


store = _make()
