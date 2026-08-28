import time
from collections import OrderedDict


class CacheManager:

    def __init__(self, max_size=3):
        self.max_size = max_size

        # OrderedDict allows us to maintain
        # the order of recently used items.
        self.cache = OrderedDict()

        # Statistics
        self.hits = 0
        self.misses = 0

    # -----------------------------------------
    # GET
    # -----------------------------------------

    def get(self, key):

        if key not in self.cache:
            self.misses += 1
            return None

        item = self.cache[key]

        # Check TTL
        if time.time() - item["timestamp"] >= item["ttl"]:

            print(f"[CACHE EXPIRED] {key}")

            del self.cache[key]

            self.misses += 1
            return None

        # LRU:
        # Move recently accessed item to the end.
        self.cache.move_to_end(key)

        self.hits += 1

        print(f"[CACHE HIT] {key}")

        return item

    # -----------------------------------------
    # PUT
    # -----------------------------------------

    def put(self, key, content, status, headers, ttl):

        # If key already exists, remove it first.
        if key in self.cache:
            del self.cache[key]

        # Store new item
        self.cache[key] = {
            "content": content,
            "status": status,
            "headers": headers,
            "timestamp": time.time(),
            "ttl": ttl
        }

        print(f"[CACHE STORE] {key} | TTL={ttl}s")

        # -----------------------------------------
        # LRU EVICTION
        # -----------------------------------------

        if len(self.cache) > self.max_size:

            # First item = least recently used
            removed_key, _ = self.cache.popitem(last=False)

            print(
                f"[LRU EVICTION] Removed: {removed_key}"
            )

    # -----------------------------------------
    # DELETE
    # -----------------------------------------

    def delete(self, key):

        if key in self.cache:
            del self.cache[key]

    # -----------------------------------------
    # CLEAR
    # -----------------------------------------

    def clear(self):

        self.cache.clear()

    # -----------------------------------------
    # STATISTICS
    # -----------------------------------------

    def stats(self):

        total_requests = self.hits + self.misses

        if total_requests > 0:
            hit_rate = (self.hits / total_requests) * 100
        else:
            hit_rate = 0

        return {
            "cache_entries": len(self.cache),
            "cache_capacity": self.max_size,
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate": round(hit_rate, 2)
        }