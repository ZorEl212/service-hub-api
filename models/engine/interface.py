# storage/abstract.py
from abc import ABC, abstractmethod
from typing import Type, Union

class AbstractStorageEngine(ABC):
    @abstractmethod
    async def all(self, cls: Union[Type, str] = None):
        pass

    @abstractmethod
    async def new(self, obj):
        pass

    @abstractmethod
    async def save(self):
        pass

    @abstractmethod
    async def reload(self):
        pass

    @abstractmethod
    async def delete(self, obj):
        pass

    @abstractmethod
    async def get(self, cls, id):
        pass

    @abstractmethod
    async def count(self, cls=None):
        pass

    @abstractmethod
    async def close(self):
        pass
