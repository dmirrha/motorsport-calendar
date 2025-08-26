import json
import sqlite3
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple, List


@dataclass
class CacheConfig:
    dir: Path
    ttl_days: int = 30
    lru_capacity: int = 10000


class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = max(1, int(capacity))
        self.data: "OrderedDict[str, Tuple[float, List[float]]]" = OrderedDict()

    def get(self, key: str) -> Optional[List[float]]:
        item = self.data.get(key)
        if item is None:
            return None
        _, value = item
        # move to end (most recently used)
        self.data.move_to_end(key)
        return value

    def put(self, key: str, value: List[float]):
        now = time.time()
        if key in self.data:
            self.data.move_to_end(key)
        self.data[key] = (now, value)
        if len(self.data) > self.capacity:
            self.data.popitem(last=False)


class DiskCache:
    def __init__(self, db_path: Path, ttl_days: int):
        self.db_path = db_path
        self.ttl_seconds = int(ttl_days) * 86400 if ttl_days >= 0 else -1
        self._init_db()

    def _connect(self):
        return sqlite3.connect(str(self.db_path))

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS embeddings (
                    k TEXT PRIMARY KEY,
                    v TEXT NOT NULL,
                    ts INTEGER NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_ts ON embeddings(ts)")
            conn.commit()

    def get(self, key: str) -> Optional[List[float]]:
        with self._connect() as conn:
            cur = conn.execute("SELECT v, ts FROM embeddings WHERE k=?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            v_json, ts = row
            if self.ttl_seconds >= 0:
                if time.time() - ts > self.ttl_seconds:
                    # expired: delete and miss
                    conn.execute("DELETE FROM embeddings WHERE k=?", (key,))
                    conn.commit()
                    return None
            try:
                return json.loads(v_json)
            except Exception:
                # corrupt entry
                conn.execute("DELETE FROM embeddings WHERE k=?", (key,))
                conn.commit()
                return None

    def put(self, key: str, value: List[float]):
        ts = int(time.time())
        v_json = json.dumps(value, separators=(",", ":"))
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO embeddings(k, v, ts) VALUES(?,?,?)",
                (key, v_json, ts),
            )
            conn.commit()


class CombinedCache:
    def __init__(self, memory: LRUCache, disk: DiskCache):
        self.memory = memory
        self.disk = disk
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[List[float]]:
        v = self.memory.get(key)
        if v is not None:
            self.hits += 1
            return v
        v = self.disk.get(key)
        if v is not None:
            # warm memory
            self.memory.put(key, v)
            self.hits += 1
            return v
        self.misses += 1
        return None

    def put(self, key: str, value: List[float]):
        self.memory.put(key, value)
        self.disk.put(key, value)


__all__ = [
    "CacheConfig",
    "LRUCache",
    "DiskCache",
    "CombinedCache",
]
