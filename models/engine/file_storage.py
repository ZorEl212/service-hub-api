#!/usr/bin/python3
"""
Contains the AsyncFileStorage class
"""
import json

from models.engine.interface import AbstractStorageEngine
from models.user import User
from typing import Union, Type
import aiofiles

classes = {"User": User}


class FileStorage(AbstractStorageEngine):
    """Asynchronously serializes instances to a JSON file & deserializes back to instances"""

    __file_path = "file.json"
    __objects = {}

    async def all(self, cls: Union[Type, str] = None):
        """returns the dictionary __objects, optionally filtered by class"""
        if cls is not None:
            new_dict = {}
            for key, value in self.__objects.items():
                if cls == value.__class__ or cls == value.__class__.__name__:
                    new_dict[key] = value
            return new_dict
        return self.__objects

    async def new(self, obj):
        """sets in __objects the obj with key <obj class name>.id"""
        if obj is not None:
            key = obj.__class__.__name__ + "." + obj.id
            self.__objects[key] = obj

    async def save(self):
        """asynchronously serializes __objects to the JSON file"""
        json_objects = {}
        for key in self.__objects:
            obj_dict = await self.__objects[key].to_dict()
            obj_dict["__class__"] = self.__objects[key].__class__.__name__
            json_objects[key] = obj_dict

        async with aiofiles.open(self.__file_path, 'w') as f:
            await f.write(json.dumps(json_objects))

    async def reload(self):
        """asynchronously deserializes the JSON file to __objects"""
        try:
            async with aiofiles.open(self.__file_path, 'r') as f:
                content = await f.read()
                jo = json.loads(content)

            for key in jo:
                class_name = jo[key]["__class__"]
                if class_name in classes:
                    self.__objects[key] = classes[class_name](**jo[key])
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Reload error: {e}")

    def delete(self, obj=None):
        """delete obj from __objects if it’s inside"""
        if obj is not None:
            key = obj.__class__.__name__ + '.' + obj.id
            if key in self.__objects:
                del self.__objects[key]

    async def close(self):
        """asynchronously reload objects from file"""
        await self.reload()

    async def get(self, cls, id):
        """asynchronously get object by class and id"""
        if cls not in classes.values():
            return None

        all_cls = await self.all(cls)
        for value in all_cls.values():
            if value.id == id:
                return value
        return None

    async def count(self, cls=None):
        """asynchronously count objects in storage"""
        if not cls:
            count = 0
            for clas in classes.values():
                count += len((await self.all(clas)).values())
        else:
            count = len((await self.all(cls)).values())
        return count
