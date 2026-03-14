from domain.models import Track
# from infrastructure.mappers import map_playback
from domain.repositories import RepoBundle

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.core import ServiceCoordinator


from .base_service import BaseService


from typing import Any, Dict, List, Optional

class PlaybackService(BaseService):
    def __init__(self, model_cls, coordinator):
        super().__init__(model_cls, coordinator)

# class PlaybackService(BaseService[Playback]):
#     def __init__(self, coordinator) -> None:
#         super().__init__(Playback, coordinator)

#     # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#     # HELPERS ═════════════════════════════════════════════════════════════════════════════════════════════════════════
#     # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#     def _normalize(self, raw_data: dict, source: RepoBundle) -> dict:
#         # return source.playback.normalize(raw_data)
#         pass
    
#     def _get_one_from_norm_raw(self, norm_data: dict) -> Playback:
#         if not norm_data:
#             return None
        
#         # playback = self._get_or_cache(norm_data['id'], lambda: map_playback(norm_data))
#         # TODO: Def doesn't make sense to cache playback, since it's only one object. Right?
#         playback = map_playback(norm_data)

#         if norm_data["track"]:
#             playback.track = self.coordinator.track_service._get_one_from_norm_raw(norm_data["track"])
        
#         return playback
    
#     # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#     # GATHERERS ═══════════════════════════════════════════════════════════════════════════════════════════════════════
#     # ═════════════════════════════════════════════════════════════════════════════════════════════════════════════════
#     # TODO: Make Sure Internal Source is not needed
#     def get_playback(self) -> Playback:
#         source = self.coordinator.ext_source
#         return self._get_one_from_raw(source.playback.get_playback())

#     def write_to_queue(self, track_ids: list[str]) -> None:
#         source = self.coordinator.ext_source
#         source.playback.write_to_queue(track_ids)

#     def change_playback(self, pause: bool | None=None, skip: str="", shuffle: bool | None=None, repeat: str="") -> None:
#         source = self.coordinator.ext_source
#         source.playback.change_playback(pause, skip, shuffle, repeat)

#     def get_recent_tracks(self) -> list[Track]:
#         source = self.coordinator.ext_source
#         raw_tracks = source.playback.get_recent_tracks()
#         return self.coordinator.track_service._get_many_from_raw(raw_tracks, source)