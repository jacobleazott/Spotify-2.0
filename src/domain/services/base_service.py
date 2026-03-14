from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.core import ServiceCoordinator


from domain.repositories import RepoBundle

from typing import Type, TypeVar, Generic, Callable, Any
from abc import ABC, abstractmethod

T = TypeVar("T")

class BaseService(Generic[T]):
    def __init__(self, model_cls: Type[T], coordinator):
        self.coordinator = coordinator
        self.model_cls = model_cls

    @abstractmethod
    def _normalize(self, raw_data: dict, source: RepoBundle) -> dict:
        pass

    @abstractmethod
    # TODO: Change to _build_from_norm_data
    def _get_one_from_norm_raw(self, norm_data: dict) -> T:
        pass
    # TODO: Change to _build_many_from_norm_data
    def _get_many_from_norm_raw(self, norm_list: list[dict]) -> list[T]:
        return [self._get_one_from_norm_raw(norm) for norm in norm_list]
    
    # TODO: Change to _build_from_raw
    def _get_one_from_raw(self, raw: dict, source: RepoBundle) -> T:
        return self._get_one_from_norm_raw(self._normalize(raw, source))

    # TODO: Change to _build_many_from_raw
    def _get_many_from_raw(self, raw_list: list[dict], source: RepoBundle) -> list[T]:
        return [self._get_one_from_raw(raw, source) for raw in raw_list]

    def _get_or_cache(self, obj_id: str, factory: Callable[[], T]) -> T:
        if cached := self.coordinator.id_map.get(self.model_cls, obj_id):
            return cached
        
        obj = factory()
        self.coordinator.id_map.set(self.model_cls, obj_id, obj)
        return obj
    
    def _get_source(self, prefer_external: bool) -> RepoBundle:
        return self.coordinator.ext_source if prefer_external else self.coordinator.int_source

    def _fetch_and_hydrate(self, fetch_fn: Callable[[RepoBundle], Any], prefer_external: bool=True) -> list[T]:
        source = self._get_source(prefer_external)
        raw_data = fetch_fn(source)
        return self._get_many_from_raw(raw_data, source)