# This is the home to "interdependent" services. Intermediaries to features that aren't specific calls to the abstract source.

def get_tracks_by_artist(self): # TODO : Move this to AppService ?
    pass


# Should probably do a base class for a lot of my services, something like this

class BaseService:
    def __init__(self, coordinator):
        self.coordinator = coordinator

    def get_source(self, prefer_external: bool):
        return self.coordinator.ext_source if prefer_external else self.coordinator.int_source

    def get_cached(self, model_cls, obj_id):
        return self.coordinator.id_map.get(model_cls, obj_id)

    def cache(self, model_cls, obj_id, obj):
        self.coordinator.id_map.set(model_cls, obj_id, obj)
