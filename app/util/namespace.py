# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta

from .hierarchied import Hierarchied

class Namespace(Hierarchied, metaclass=ABCMeta):
    """
    Class implementing a namespace that can be accessed like a dictionary or using attributes
    """

    # If True, then attributes that do not exist return None by default
    DEFAULT_TO_NONE = False

    # If not None, must be a tuple of allowed fields
    FIELDS = None
    # Same as FIELDS, but these fields must never be None
    FIELDS_NOT_NONE = None

    # If set to True, this Namespace will automatically convert dictionaries into namespaces
    STICKY = False
    # If not None, this delimiter will cause IS_STICKY=True to also split keys with this delimiter
    STICKY_DELIMITER = None
    # If True, STICK=TRUE will eagerly convert values into namespace by calling 'to_dict' if it exists
    STICKY_EAGER = False

    # If True, allows changing private attributes when frozen
    FROZEN_ALLOW_PRIVATE = False


    # Constructor
    def __init__(self, log_name=None, parent=None, frozen=False, **kwargs):
        super().__init__(log_name=log_name, parent=parent)

        self._hash     = None
        self._frozen   = False

        self._dict     = {}
        self.merge(kwargs)

        self._initialize_fields()

        self._frozen   = frozen


    def _has_fixed_fields(self):
        return self.__class__.FIELDS is not None or self.__class__.FIELDS_NOT_NONE is not None

    def _is_field(self, name):
        if not self._has_fixed_fields():
            return True

        fields          = self.__class__.FIELDS          or ()
        fields_not_none = self.__class__.FIELDS_NOT_NONE or ()

        return name in fields or name in fields_not_none

    def _initialize_fields(self):
        if not self._has_fixed_fields():
            return

        for k in self.__class__.FIELDS_NOT_NONE or ():
            if getattr(self, k, None) is None:
                raise ValueError(f"{self.__class__.__name__} does not allow field '{k}' to be None")


    # Adding to the namespace
    def _sanity_check_key(self, key : str, *, delete=False):
        if not key:
            raise ValueError(f"key must be defined")
        elif not self._is_field(key):
            raise ValueError(f"{self.__class__.__name__} does not contain field '{key}'")

    def _get_write_target(self, key):
        return self

    def _set(self, key : str, value):
        """ Add a new attribute."""

        # Handle @property.setter
        if hasattr(self.__class__, key):
            attr = getattr(self.__class__, key)
            if isinstance(attr, property):
                attr.fset(self, value)
                return value

        # Sanity checks
        if self.frozen:
            raise TypeError(f"{repr(self)} is frozen")
        self._sanity_check_key(key)

        # Sticky
        if self.__class__.STICKY:
            if self.__class__.STICKY_DELIMITER is not None:
                split_key = key.split(self.__class__.STICKY_DELIMITER, 1)
                if len(split_key) > 1:
                    key     = split_key[0]
                    sub_key = split_key[1]
                    self._sanity_check_key(key)
                    value = self._sticky_create_namespace(key, sub_key, value)

            if isinstance(value, dict):
                value = self._sticky_create_namespace(key, None, value)
            elif not isinstance(value, Namespace) and hasattr(value, 'to_dict'):
                value = self._sticky_create_namespace(key, None, value.to_dict())

        # Handle custom target
        if not self.__class__.STICKY or not isinstance(value, Namespace):
            tgt : Namespace = self._get_write_target(key)
            if tgt is not self:
                return tgt._set(key, value)

        # Check if field can be None
        if value is None:
            fields_not_none = self.__class__.FIELDS_NOT_NONE or ()
            if key in fields_not_none:
                raise ValueError(f"{self.__class__.__name__} does not allow field '{key}' to be None")

        # Add to dictionary
        self._hash = None
        self._dict[key] = value
        return value

    def _set_private(self, key: str, value):
        if key != '_frozen' and not self.__class__.FROZEN_ALLOW_PRIVATE and self.frozen:
            raise TypeError(f"{repr(self)} is frozen")

        self.__dict__[key] = value
        return value

    def _remove(self, key, fail=True):
        """ Remove an attribute.
        Keys may not start with '_' """

        # Sanity checks
        if self.frozen:
            raise TypeError(f"{repr(self)} is frozen")
        self._sanity_check_key(key, delete=True)

        # Sticky
        if self.__class__.STICKY and self.__class__.STICKY_DELIMITER is not None:
            split_key = key.split(self.__class__.STICKY_DELIMITER, 1)
            if len(split_key) > 1:
                self_key = split_key[0]
                sub_key  = split_key[1]
                self._sanity_check_key(self_key, delete=True)

                sub_namespace : Namespace = self[self_key]
                sticky_cls = self._sticky_namespace_class()
                if not isinstance(sub_namespace, sticky_cls):
                    raise ValueError(f"Cannot delete delimited key '{key}', as '{self_key}' is not a member of class '{sticky_cls.__name__}")

                sub_namespace._remove(sub_key)
                return

        # Handle custom target
        tgt : Namespace = self._get_write_target(key)
        if tgt is not self:
            tgt._remove(key)
            return

        # Remove from dictionary
        self._hash = None
        try:
            del self._dict[key]
        except KeyError:
            if fail:
                raise

    def _remove_private(self, key: str, fail=True):
        if not self.__class__.FROZEN_ALLOW_PRIVATE and self.frozen:
            raise TypeError(f"{repr(self)} is frozen")

        try:
            del self.__dict__[key]
        except KeyError:
            if fail:
                raise

    def _sticky_construct_namespace(self, key):
        return Namespace(log_name=key, parent=self)

    def _sticky_create_namespace(self, key, sub_key, value):
        inst = self._sticky_construct_namespace(key)

        if sub_key is None:
            inst.merge(value)
        else:
            inst[sub_key] = value

        return inst


    # Dictionary behaviour
    NO_DEFAULT = object()

    def _get_read_target(self, key):
        return self

    def _get(self, key : str, default=NO_DEFAULT):
        tgt : Namespace = self._get_read_target(key)
        if tgt is not self:
            return tgt._get(key, default=default)

        if not self._is_field(key):
            raise ValueError(f"{self.__class__.__name__} does not contain field '{key}'")

        if default is Namespace.NO_DEFAULT and self.__class__.DEFAULT_TO_NONE:
            default = None

        """ Get an entry from the internal dictionary """
        if default is Namespace.NO_DEFAULT:
            return self._dict[key]
        else:
            return self._dict.get(key, default)

    def get(self, key : str, default=NO_DEFAULT):
        return self._get(key, default=default)

    def __getitem__(self, key : str):
        """ Get an attribute using dictionary syntax obj[key] """
        if key is None or key[0] == '_':
            raise KeyError(key)
        return self._get(key)

    def __setitem__(self, key : str, value):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        if key is None or key[0] == '_':
            raise KeyError(key)
        self._set(key, value)

    def __delitem__(self, key : str):
        """ Delete an attribute using dictionary syntax """
        if key is None or key[0] == '_':
            raise KeyError(key)
        self._remove(key)

    def __getattr__(self, key : str):
        """ Get an attribute, redirected to the internal dictionary """
        try:
            if key and key[0] == '_':
                return self.__dict__[key]
            else:
                return self._get(key)
        except KeyError:
            raise AttributeError(f"Attribute '{key}' does not exist")

    def __setattr__(self, key : str, value):
        """ Set an attribute, redirected to the internal dictionary """
        if key and key[0] == '_':
            self._set_private(key, value)
        else:
            self._set(key, value)

    def __delattr__(self, key):
        """ Delete an attribute using attribute syntax """
        if key and key[0] == '_':
            self._remove_private(key)
        else:
            self._remove(key)

    def __contains__(self, m):
        return self._get(m, default=None) is not None


    # Iteration
    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        return iter(self._dict)

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self._dict)

    def keys(self):
        if self._has_fixed_fields() and self.__class__.DEFAULT_TO_NONE:
            for k in (self.__class__.FIELDS or ()) + (self.__class__.FIELDS_NOT_NONE or ()):
                yield k
            return

        for k in self._dict.keys():
            yield k

    def items(self):
        if self._has_fixed_fields() and self.__class__.DEFAULT_TO_NONE:
            for k in self.keys():
                yield k, self[k]
            return

        for k, v in self._dict.items():
            yield k, v

    def values(self):
        if self._has_fixed_fields() and self.__class__.DEFAULT_TO_NONE:
            for k in self.keys():
                yield self[k]
            return

        for val in self._dict.values():
            yield val


    # Comparison
    def __eq__(self, other):
        return self is other
        # return hash(self) == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)
        # return hash(self) != hash(other)

    def __hash__(self):
        """ Calculates a hash of the internal dictionary """
        return id(self)
        # if self._hash is None:
        #     hashes = map(hash, self.items())
        #     self._hash = functools.reduce(operator.xor, hashes, 0)
        # return self._hash


    # Freezing
    def freeze(self, recursive=False, temporary=False):
        """ Freezes this object, so new attributes cannot be added """
        if temporary:
            return self.__class__.TemporaryFreeze(self, True, recursive)
        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen') and not obj.frozen:
                    obj.freeze()
        self._frozen = True

    def unfreeze(self, recursive=False, temporary=False):
        """ Unfreezes this object, so new attributes can be added """
        if temporary:
            return self.__class__.TemporaryFreeze(self, False, recursive)
        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen') and obj.frozen:
                    obj.unfreeze()
        self._frozen = False

    class TemporaryFreeze(object):
        def __init__(self, obj, freeze, recursive):
            self.obj = obj
            self.freeze = freeze
            self.recursive = recursive

            if self.freeze:
                self.obj.freeze(recursive=self.recursive)
            else:
                self.obj.unfreeze(recursive=self.recursive)

        def __enter__(self):
            pass

        def __exit__(self, _, __, ___):
            if self.freeze:
                self.obj.unfreeze(recursive=self.recursive)
            else:
                self.obj.freeze(recursive=self.recursive)

    @property
    def frozen(self):
        return self.__dict__.get('_frozen', False)
    @frozen.setter
    def frozen(self, val):
        if val:
            self.freeze()
        else:
            self.unfreeze()


    # Utilities
    def to_dict(self, recursive=True):
        if not recursive:
            return dict(self._dict)

        d = {}
        for k, v in self._dict.items():
            if isinstance(v, Namespace):
                v = v.to_dict(recursive=recursive)
            d[k] = v
        return d

    def merge(self, d):
        for k, v in d.items():
            self[k] = v


    # Printing
    def __repr__(self):
        return f"<{self._repr_name}:{repr(self._dict)},{repr(self.__dict__)}>"

    def repr_dict(self):
        return repr(self._dict)
