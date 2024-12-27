import os
from collections import OrderedDict

CACHE_DIR = "./cache"  # directory to store cached files
BUFFER_SIZE = 4096  # Size for data chunks

class LRUCache:
    def __init__(self, capacity):
        self.cache = OrderedDict()
        self.capacity = capacity

        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
    def retreive_from_cache(self, key):
        """ retrieve data from the cache."""
        if key in self.cache:
            # move to the end to mark as recently used
            self.cache.move_to_end(key)
            path = os.path.join(CACHE_DIR, key)
            if os.path.exists(path):
                with open(path, "rb") as f:
                    return f.read()
        return None

    def insert_into_cache(self, key, data):
        """ add data to the cache with LRU eviction """
        if key in self.cache:
            self.cache.move_to_end(key)
        elif len(self.cache) >= self.capacity:
            # remove the least recently used item
            old_key, _ = self.cache.popitem(last=False) #FIFO
            os.remove(os.path.join(CACHE_DIR, old_key))
            print(f"Evicting {old_key} from cache due to size limit.")

        # add new data to cache
        self.cache[key] = True
        with open(os.path.join(CACHE_DIR, key), "wb") as file:
            file.write(data)

        