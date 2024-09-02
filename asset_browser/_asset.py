from dataclasses import dataclass, fields, field
from typing import List, Any, Dict

from enum import Enum
from functools import partial

class AssetType(Enum):
    CHARACTER = 0
    PROP = 1


class AssetDataType(Enum):
    ENTITY = 0
    VERSION = 1
    URI = 2
    LOD = 3

class LazyAttribute:
    def __init__(self, func):
        self.func = func
        self.cache_name = f"_{func.__name__}_cache"
        self.__cached = False

    def __get__(self, instance, owner):
        if instance is None:
            return self
        
        # Check if the result is already cached
        if self.__cached:
            return getattr(instance, self.cache_name)
        
        # Compute the value, cache it, and return
        result = self.func(instance)
        setattr(instance, self.cache_name, result)
        return result

    def clear_cache(self, instance):
        """Clear the cached value."""
        self.__cached = False
        if hasattr(instance, self.cache_name):
            delattr(instance, self.cache_name)

class ClassLazyAttribute:
    _cache = {}  # Class-level cache

    def __init__(self, func, key_func):
        self.func = func
        self.key_func = key_func

    def __get__(self, instance, owner):
        print(f"in get {instance}  {owner}")
        if instance is None:
            return self
        
        # Use the instance's name as the key
        key = self.key_func(instance)

        # If the value is already cached, return it
        if key in self._cache:
            return self._cache[key]
        
        # Compute the value, cache it, and return
        result = self.func(self.key_func)
        self._cache[key] = result
        return result

    def clear_cache(self, key=None):
        """Clear the cached value for a specific key or all keys."""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

# maybe decorate this with lru cache
def get_asset_versions(*args, **kwargs):
    # slow function such as datebase query
    print(f'in get_asset_ver {args} {kwargs}')

@dataclass
class AssetDef:
    _type: AssetType = field(metadata={"ui_name": "T", "visible":True})
    entity: AssetDataType.ENTITY = field(metadata={"ui_name": "Entity", "visible":True})
    version: AssetDataType.VERSION = field(metadata={"ui_name": "Version", "visible":True, "affect": ("lod",)})
    lod: AssetDataType.LOD = field(default='lo', metadata={"ui_name": "LOD", "visible":True})

    # define lazy attrs
    versions = ClassLazyAttribute(get_asset_versions, lambda inst: inst.entity)

    def __post_init__(self):
        self._dirty = False
        self._original_values = {
            field.name: getattr(self, field.name) for field in fields(self)
        }
        self._dirty_fields = {}

        # init lazy attrs

    def __setattr__(self, name: str, value: Any) -> None:
        if name in getattr(self, "_original_values", {}):
            if self._original_values[name] != value:
                self._dirty = True
                self._dirty_fields[name] = value
            elif name in self._dirty_fields:
                del self._dirty_fields[name]
                if not self._dirty_fields:
                    self._dirty = False
        super().__setattr__(name, value)

    @property
    def dirty(self):
        return self._dirty

    @property
    def attributes(self):
        return {field.name: getattr(self, field.name) for field in fields(self)}

    def isAttrDirty(self, attr):
        return attr in self._dirty_fields
    
    @property
    def dirtyAttrs(self):
        return self._dirty_fields
    
    def reset(self):
        if not self.dirty:
            return
        for f in fields(self):
            if self._original_values[f.name] != getattr(self, f.name):
                setattr(self,f.name, self._original_values[f.name] )
                print(f'reset {f.name} to {self._original_values[f.name]}')

# @dataclass
# class Asset(AssetDef):
#     version: int = 10
#     # lod = 'lo'


# a = Asset(_type=AssetType.CHARACTER, version=20, entity='han')

if __name__ == '__main__':
    print('yes')
    import random, names
    asset = \
            AssetDef(
                _type=random.choice(list(AssetType)),
                version=random.randint(1, 20),
                entity=names.get_first_name(),
                lod = random.choice(('lo','hi'))
            )
    asset.versions