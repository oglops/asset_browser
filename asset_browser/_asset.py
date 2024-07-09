from dataclasses import dataclass, fields, field
from typing import List, Any, Dict

from enum import Enum


class AssetType(Enum):
    CHARACTER = 0
    PROP = 1


class AssetDataType(Enum):
    ENTITY = 0
    VERSION = 1
    URI = 2
    LOD = 3


@dataclass
class AssetDef:
    _type: AssetType = field(metadata={"visible": False, "ui_name": "Type"})
    entity: AssetDataType.ENTITY = field(metadata={"ui_name": "Entity"})
    version: AssetDataType.VERSION = field(metadata={"ui_name": "Version", "affect": ("lod",)})
    lod: AssetDataType.LOD = field(default='lo', metadata={"ui_name": "LOD", })

    def __post_init__(self):
        self._dirty = False
        self._original_values = {
            field.name: getattr(self, field.name) for field in fields(self)
        }
        self._dirty_fields = {}

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
