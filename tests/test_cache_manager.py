import importlib
import sys
import types

import pytest

class DummyRedis:
    def __init__(self, *args, **kwargs):
        self.store = {}
    def ping(self):
        return True
    def setex(self, key, ttl, value):
        self.store[key] = value
    def get(self, key):
        return self.store.get(key)
    def keys(self, pattern):
        if pattern.endswith('*'):
            prefix = pattern[:-1]
            return [k for k in self.store if k.startswith(prefix)]
        return [k for k in self.store if k == pattern]
    def delete(self, *keys):
        count = 0
        for k in keys:
            if k in self.store:
                del self.store[k]
                count += 1
        return count
    def incr(self, key):
        self.store[key] = int(self.store.get(key, 0)) + 1
        return self.store[key]
    def info(self):
        return {"connected_clients": 1, "used_memory_human": "1MB"}
    def dbsize(self):
        return len(self.store)

def import_cache(monkeypatch):
    from pathlib import Path
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    fake_module = types.ModuleType('redis')
    fake_module.Redis = DummyRedis
    monkeypatch.setitem(sys.modules, 'redis', fake_module)
    return importlib.import_module('backend.app.cache')

@pytest.fixture
def cache(monkeypatch):
    cache_module = import_cache(monkeypatch)
    return cache_module.CacheManager()

def test_set_and_get(cache):
    key = cache.generate_key('question', 'ctx')
    assert cache.set(key, {'a': 1})
    assert cache.get(key) == {'a': 1}

def test_delete_and_stats(cache):
    k1 = cache.generate_key('q1')
    k2 = cache.generate_key('q2')
    cache.set(k1, {'v': 1})
    cache.set(k2, {'v': 2})
    assert cache.delete('*') == 2
    assert cache.get(k1) is None
    cache.increment_stat('hits')
    assert cache.get_stats()['total_queries'] == 0  # unaffected
    assert cache.get_stats()['cache_hits'] == 0
