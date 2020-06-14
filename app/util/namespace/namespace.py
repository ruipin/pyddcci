# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any
from dataclasses import is_dataclass, asdict as dataclass_asdict

from .. import LoggableMixin, HierarchicalMixin, NamedMixin
from ..enter_exit_call import EnterExitCall


class Namespace(object):
    """
    Class implementing a namespace that can be accessed like a dictionary or using attributes
    """

    # We want to hide some attributes from the dictionary
    # NOTE: We include the log/parent attributes here just in case someone decides to make this class Loggable or Hierarchical
    __slots__ = {'_Namespace__frozen_namespace', '_Namespace__frozen_schema', '_Namespace__namespace', '_NamedMixin__name', '_HierarchicalMixin__parent',
                 '_LoggableMixin__log'}


    # Default value for parameters to signal that the function should fail
    NO_DEFAULT = object()


    """ Customizable class attributes """
    # If True, then attributes that do not exist return None by default
    NAMESPACE__DEFAULT = NO_DEFAULT

    # If True, allows changing private attributes when the namespace is frozen
    NAMESPACE__FROZEN_NAMESPACE__ALLOW_PRIVATE = False
    # If True, allows changing private attributes when the schema is frozen
    NAMESPACE__FROZEN_SCHEMA__ALLOW_PRIVATE = False

    # If set to True, this Namespace will automatically convert dictionaries into namespaces
    NAMESPACE__STICKY = False
    # If not None, this delimiter will cause STICKY=True to also split keys with this delimiter
    NAMESPACE__STICKY__DELIMITER = None

    # Constructor
    def __init__(self, *, frozen_schema=False, frozen_namespace=False, **kwargs):
        # Sanity check: We must come before Named/Hierarchical/Loggable
        def _check_mro(mro, mixin):
            if mixin in mro and mro.index(mixin) < mro.index(Namespace):
                raise TypeError(f"'Namespace' must come *before* '{mixin}' in the MRO")
        mro = self.__class__.__mro__
        _check_mro(mro, NamedMixin)
        _check_mro(mro, HierarchicalMixin)
        _check_mro(mro, LoggableMixin)

        # Initialize basic state before calling super constructors
        self.__frozen_schema    = False
        self.__frozen_namespace = False

        self.__namespace = {}

        # Call super-class
        super_params = {}
        if isinstance(self, NamedMixin):
            super_params['instance_name'] = kwargs.pop('instance_name', None)
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = kwargs.pop('instance_parent', None)
        super().__init__(**super_params)

        # Finish initialization
        if kwargs:
            self.merge(kwargs)

        self.__frozen_schema    = frozen_schema
        self.__frozen_namespace = frozen_namespace


    # Utilities
    def __sanity_check_key(self, key : str, *, delete: bool =False) -> bool:
        if not key:
            raise ValueError(f"key must be defined")

    def __is_frozen_key(self, key : str) -> bool:
        if self.frozen_namespace:
            if not self.__class__.NAMESPACE__FROZEN_SCHEMA__ALLOW_PRIVATE or not key or key[0] != '_':
                return True

        if not self.frozen_schema:
            return False

        if key in self.__namespace:
            return False

        if self.__class__.NAMESPACE__FROZEN_SCHEMA__ALLOW_PRIVATE and key and key[0] == '_':
            return False

        return True

    def __is_slots_key(self, key : str) -> bool:
        return key in Namespace.__slots__

    def __get_access_dict(self, key : str) -> dict:
        return self.__namespace


    # Adding to the namespace
    def __get_write_target(self, key : str) -> 'Namespace':
        return self

    def __set(self, key : str, value : Any) -> Any:
        """ Add a new attribute."""

        # Handle a __slots__ keys
        if self.__is_slots_key(key):
            return super().__setattr__(key, value)

        # Handle @property.setter
        if hasattr(self.__class__, key):
            attr = getattr(self.__class__, key)
            if isinstance(attr, property):
                attr.__set__(self, value)
                return value

        # Sanity checks
        if self.__is_frozen_key(key):
            raise TypeError(f"{str(self)} is frozen, can't add key '{key}'")
        self.__sanity_check_key(key)

        # Sticky
        if self.__class__.NAMESPACE__STICKY and not self._sticky_ignore_key(key):
            if self.__class__.NAMESPACE__STICKY__DELIMITER is not None:
                split_key = key.split(self.__class__.NAMESPACE__STICKY__DELIMITER, 1)
                if len(split_key) > 1:
                    key     = split_key[0]
                    sub_key = split_key[1]
                    self._sanity_check_key(key)

                    if key in self:
                        self[key][sub_key] = value
                        return

                    value = self.__sticky_create_namespace(key, sub_key, value)

            if isinstance(value, dict):
                value = self.__sticky_create_namespace(key, None, value)
            elif not isinstance(value, Namespace) and hasattr(value, 'asdict'):
                value = self.__sticky_create_namespace(key, None, value.asdict())

        # Handle custom target
        if not self.__class__.NAMESPACE__STICKY or not isinstance(value, Namespace):
            tgt : Namespace = self.__get_write_target(key)
            if tgt is not self:
                return tgt.__set(key, value)

        # Add to dictionary
        self.__get_access_dict(key)[key] = value
        return value

    def __remove(self, key, fail=True):
        """ Remove an attribute."""

        # Handle a __slots__ key
        if self.__is_slots_key(key):
            return super.__delattr__(key)

        # Sanity checks
        if self.__is_frozen_key(key):
            raise TypeError(f"{repr(self)} is frozen, can't delete key '{key}'")
        self.__sanity_check_key(key, delete=True)

        # Sticky
        if self.__class__.NAMESPACE__STICKY and not self._sticky_ignore_key(key):
            if self.__class__.NAMESPACE__STICKY__DELIMITER is not None:
                split_key = key.split(self.__class__.NAMESPACE__STICKY__DELIMITER, 1)
                if len(split_key) > 1:
                    self_key = split_key[0]
                    sub_key  = split_key[1]
                    self.__sanity_check_key(self_key, delete=True)

                    sub_namespace : Namespace = self[self_key]
                    if not isinstance(sub_namespace, Namespace):
                        raise ValueError(f"Cannot delete delimited key '{key}', as '{self_key}' is not a member of class '{self._sticky_construct_class().__name__}")

                    sub_namespace.__remove(sub_key)
                    return

        # Handle custom target
        tgt : Namespace = self.__get_write_target(key)
        if tgt is not self:
            tgt.__remove(key)
            return

        # Remove from dictionary
        try:
            del self.__get_access_dict(key)[key]
        except KeyError:
            if fail:
                raise


    # Reading from Namespace
    def __get_read_target(self, key):
        return self

    def __get(self, key : str, default=NO_DEFAULT):
        # Handle a __slots__ key
        if self.__is_slots_key(key):
            return super().__getattr__(key)

        # Handle default value
        if default is Namespace.NO_DEFAULT:
            default = self.__class__.NAMESPACE__DEFAULT

        # Sticky
        if self.__class__.NAMESPACE__STICKY and not self._sticky_ignore_key(key):
            if self.__class__.NAMESPACE__STICKY__DELIMITER is not None:
                split_key = key.split(self.__class__.NAMESPACE__STICKY__DELIMITER, 1)
                if len(split_key) > 1:
                    self_key = split_key[0]
                    sub_key = split_key[1]
                    self.__sanity_check_key(self_key, delete=True)

                    if self_key not in self:
                        if default is Namespace.NO_DEFAULT:
                            raise KeyError()
                        else:
                            return default

                    return self[self_key][sub_key]

        # Handle custom target
        tgt: Namespace = self.__get_read_target(key)
        if tgt is not self:
            return tgt.__get(key, default=default)

        """ Get an entry from the internal dictionary """
        d = self.__get_access_dict(key)
        if default is Namespace.NO_DEFAULT:
            return d[key]
        else:
            return d.get(key, default)


    # Sticky
    @classmethod
    def _sticky_construct_class(cls) -> type:
        return cls

    def __sticky_construct_namespace(self, key):
        super_params = {}
        if isinstance(self, HierarchicalMixin):
            super_params['instance_parent'] = self
        if isinstance(self, NamedMixin):
            super_params['instance_name'] = key
        super_params['frozen_schema'] = self.frozen_schema

        return self._sticky_construct_class()(**super_params)

    def __sticky_create_namespace(self, key, sub_key, value):
        inst = self.__sticky_construct_namespace(key)

        if sub_key is None:
            inst.merge(value)
        else:
            inst[sub_key] = value

        return inst

    def _sticky_ignore_key(self, key : str) -> bool:
        return False


    # Dictionary Magic Methods
    def __getitem__(self, key : str):
        """ Get an attribute using dictionary syntax obj[key] """
        if self.__is_slots_key(key):
            raise KeyError
        return self.__get(key)

    def __setitem__(self, key : str, value):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        if self.__is_slots_key(key):
            raise KeyError
        self.__set(key, value)

    def __delitem__(self, key : str):
        """ Delete an attribute using dictionary syntax """
        if self.__is_slots_key(key):
            raise KeyError
        self.__remove(key)

    def __contains__(self, m):
        try:
            self.__getitem__(m)
            return True
        except KeyError:
            return False


    # Attribute Magic Methods
    def __getattr__(self, key : str):
        """ Get an attribute, redirected to the internal dictionary """
        try:
            return self.__get(key)
        except KeyError:
            raise AttributeError(f"Attribute '{key}' does not exist")

    def __setattr__(self, key : str, value):
        """ Set an attribute, redirected to the internal dictionary """
        self.__set(key, value)

    def __delattr__(self, key):
        """ Delete an attribute using attribute syntax """
        self.__remove(key)


    # Iteration
    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        return iter(self.__namespace)

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self.__namespace)

    def __keys(self):
        return self.__namespace.keys()

    def __items(self):
        return self.__namespace.items()

    def __values(self):
        return self.__namespace.values()


    # Comparison
    def __eq__(self, other):
        return self is other
        # return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
        # return hash(self) != hash(other)

    def __hash__(self):
        """ We just return the id which is guaranteed to be unique per object """
        return id(self)


    # Freezing
    def freeze_schema(self, freeze=True, *, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return EnterExitCall(
                self.freeze_schema, self.freeze_schema,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen_schema') and obj.frozen_schema != freeze:
                    obj.freeze_schema(freeze=freeze, recursive=True, temporary=False)

        self.__frozen_schema = freeze

    def unfreeze_schema(self, recursive=False, temporary=False):
        return self.freeze_schema(False, recursive=recursive, temporary=temporary)

    @property
    def frozen_schema(self):
        return self.__frozen_schema
    @frozen_schema.setter
    def frozen_schema(self, val):
        self.freeze_schema(val, temporary=False)


    def freeze_namespace(self, freeze=True, *, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return EnterExitCall(
                self.freeze_namespace, self.freeze_namespace,
                kwargs_enter={'freeze': freeze, 'recursive': recursive, 'temporary': False},
                kwargs_exit={'freeze': not freeze, 'recursive': recursive, 'temporary': False})

        if recursive:
            for obj in self.values():
                if hasattr(obj, 'freeze_namespace') and obj.freeze_namespace != freeze:
                    obj.freeze_namespace(freeze=freeze, recursive=True, temporary=False)

        self.__frozen_namespace = freeze

    def unfreeze_namespace(self, recursive=False, temporary=False):
        return self.freeze_schema(False, recursive=recursive, temporary=temporary)

    @property
    def frozen_namespace(self):
        return self.__frozen_namespace
    @frozen_namespace.setter
    def frozen_namespace(self, val):
        self.freeze_namespace(val, temporary=False)


    # Utilities
    def asdict(self, recursive=True, private=False, protected=True, public=True):
        d = {}
        for k, v in self.__namespace.items():
            if k[0] == '_':
                if '__' in k:
                    if not private:
                        continue
                elif not protected:
                    continue

            if k[0] != '_' and not public:
                continue

            if recursive:
                if isinstance(v, Namespace):
                    v = v.asdict(recursive=recursive, private=private, protected=protected, public=public)

                if not private and is_dataclass(v) and not isinstance(v, type):
                    v = dataclass_asdict(v)

            d[k] = v

        return d

    def merge(self, d):
        for k, v in d.items():
            self[k] = v


    # Printing
    @property
    def __repr_name(self):
        if isinstance(self, LoggableMixin):
            return self._LoggableMixin__repr_name
        if isinstance(self, HierarchicalMixin):
            return self._HierarchicalMixin__repr_name
        return self.__class__.__name__

    def __repr__(self):
        return f"<{self.__repr_name}{repr(self.asdict(recursive=False))}>"
