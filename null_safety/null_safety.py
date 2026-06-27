from functools import partial, wraps
from inspect import getmembers_static, isfunction, ismethod, ismethoddescriptor
from typing import Any

class NonValue:
    def __getattribute__(self, name):
        return Null

nonValue = NonValue()

class Value:
    def __init__(self, owner=None):
        self.owner = owner

    def __get__(self, obj=None, cls=None):
        return obj if obj else cls
    
    def __getattribute__(self, name: str) -> Any:
        if name == 'owner':
            return super().__getattribute__(name)
        elif (owner := super().__getattribute__('owner')) is not None:
            return getattr(owner, name)
        else:
            return super().__getattribute__(name)

class NullType:
    def __str__(self):
        return 'Null'

    def __repr__(self) -> str:
        return 'Null'
    
    def __bool__(self):
        return False
    
    def __getattribute__(self, name: str) -> Any:
        if name == 'ifn':
            return nonValue
        else:
            try:
                return getattr(None, name)
            except AttributeError as e:
                raise AttributeError(e.args[0].replace('NoneType', 'NullType'), *e.args[1:], name=e.name, obj=Null)

Null = NullType()


def wrapped(f, *args, **kwargs):
    return nullable(f(*args, **kwargs))

class NullableSpecialMethod:
    __slots__ = ('base_descriptor', )
    
    def __init__(self, base_descriptor):
        self.base_descriptor = base_descriptor

    def __get__(self, obj:'NullableObject | None'=None, cls=None):
        if obj is not None:
            return self.base_descriptor.__get__(obj.obj, obj.obj.__class__)
        else:
            return self.base_descriptor

class NullableObject:
    def __getattribute__(self, name: str) -> Any:
        if name == 'ifn':
            return object.__getattribute__(self, 'value')
        elif name in ('obj', 'value'):
            return object.__getattribute__(self, name)
        else:
            attr = getattr(object.__getattribute__(self, 'obj'), name)
            if callable(attr):
                return partial(wrapped, attr)
            else:
                return nullable(attr)

def nullable_object(obj: object, value: Value):
    new_obj = object.__new__(type(f'nullable<{obj.__class__.__name__}>',
                                (NullableObject,), 
                                {attr: NullableSpecialMethod(value) for attr, value in getmembers_static(obj, ismethoddescriptor) if attr.startswith('__') and attr.endswith('__')} |
                                {'__getattribute__': NullableObject.__getattribute__, 'obj': obj, 'value': value}))
    return new_obj
    

class NullableClass:
    def __init__(self, cls: type, value: Value = Value()):
        self.cls = cls
        self.value = value

    def __call__(self, *args, **kwargs):
        return nullable(self.cls(*args, **kwargs))
    
    def __getattribute__(self, name: str) -> Any:
        if name == 'ifn':
            return object.__getattribute__(self, 'value')
        elif name in ('cls', 'value'):
            return object.__getattribute__(self, name)
        else:
            attr = getattr(object.__getattribute__(self, 'cls'), name)
            if callable(attr):
                return partial(wrapped, attr)
            else:
                return nullable(attr)
    

class nullable:
    def __new__(cls, maybe_obj_or_class):
        if maybe_obj_or_class is None or maybe_obj_or_class is Null:
            return Null
        elif isinstance(maybe_obj_or_class, type):
            try:
                maybe_obj_or_class.ifn = Value()
            except TypeError:
                return NullableClass(maybe_obj_or_class, Value())
            else:
                return maybe_obj_or_class
        else:
            value_obj = Value(maybe_obj_or_class)
            try:
                maybe_obj_or_class.ifn = value_obj
            except AttributeError:
                return nullable_object(maybe_obj_or_class, value_obj)
            else:
                return maybe_obj_or_class

def undo_nullable(obj_or_class):
    if obj_or_class is None or obj_or_class is Null:
        return None
    if isinstance(obj_or_class, NullableObject):
        return obj_or_class.obj
    if isinstance(obj_or_class, NullableClass):
        return obj_or_class.cls
    return obj_or_class
    