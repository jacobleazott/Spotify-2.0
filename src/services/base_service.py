from src.services.coordinator import Coordinator
from src.sources.abstract_source import AbstractSource

from typing import Type, TypeVar, Generic, Callable, Any
from abc import ABC, abstractmethod

T = TypeVar("T")

class BaseService(Generic[T]):
    def __init__(self, model_cls: Type[T], coordinator: Coordinator):
        self.coordinator = coordinator
        self.model_cls = model_cls

    @abstractmethod
    def normalize_raw(self, raw_data: dict, source: AbstractSource) -> dict:
        pass

    @abstractmethod
    def get_one_from_norm_raw(self, norm_data: dict) -> T:
        pass

    def get_many_from_norm_raw(self, norm_list: list[dict]) -> list[T]:
        return [self.get_one_from_norm_raw(norm) for norm in norm_list]
    
    def _get_one_from_raw(self, raw: dict, source: AbstractSource) -> T:
        return self.get_one_from_norm_raw(self.normalize_raw(raw, source))

    def _get_many_from_raw(self, raw_list: list[dict], source: AbstractSource) -> list[T]:
        return [self._get_one_from_raw(raw, source) for raw in raw_list]

    def get_or_cache(self, obj_id: str, factory: Callable[[], T]) -> T:
        if cached := self.coordinator.id_map.get(self.model_cls, obj_id):
            return cached
        
        obj = factory()
        self.coordinator.id_map.set(self.model_cls, obj_id, obj)
        return obj
    
    def get_source(self, prefer_external: bool) -> AbstractSource:
        return self.coordinator.ext_source if prefer_external else self.coordinator.int_source

    def _fetch_and_hydrate(self, fetch_fn: Callable[[AbstractSource], Any], prefer_external: bool=True) -> list[T]:
        source = self.get_source(prefer_external)
        raw_data = fetch_fn(source)
        return self._get_many_from_raw(raw_data, source)