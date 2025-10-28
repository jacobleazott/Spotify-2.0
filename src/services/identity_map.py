class IdentityMap:
    def __init__(self):
        # keys: (cls, id) -> instance
        self._store: dict[tuple[type, str], object] = {}

    def get(self, cls, id_):
        return self._store.get((cls, id_))

    def add(self, cls, id_, instance):
        self._store[(cls, id_)] = instance

    def exists(self, cls, id_):
        return (cls, id_) in self._store
