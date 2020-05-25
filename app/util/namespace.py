# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta

class Namespace(object, metaclass=ABCMeta):
    """
    Class implementing a namespace that can be accessed like a dictionary or using attributes

    Classes inheriting should make sure they inherit __slots__, e.g.
    >>> __slots__ = Namespace.__slots__

    To add new slots, make sure to also inherit the existing slots, e.g.
    >>> __slots__ = set.union({'_banana'}, Namespace.__slots__)
    """

    # Tell Python to omit the built-in __dict__
    __slots__ = {'_dict', '_hash', '_log', '_log_name', '_frozen', '_parent'}

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

    # If True, allows changing the parent when frozen
    FROZEN_ALLOW_SET_PARENT = False
    # If True, allows changing the log name when frozen
    FROZEN_ALLOW_SET_LOG_NAME = False


    # Constructor
    def __init__(self, log_name=None, parent=None, frozen=False, **kwargs):
        self._hash     = None
        self._log_name = self.__class__.__name__ if log_name is None else log_name
        self._log      = None
        self._frozen   = False
        self._parent   = parent

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
        elif key[0] == '_' and key in self.__class__.__slots__:
            raise ValueError(f"key='{key}' is reserved")
        elif key[0] != '_' and f"_{key}" in self.__class__.__slots__:
            raise ValueError(f"key='{key}' is reserved")
        elif not self._is_field(key):
            raise ValueError(f"{self.__class__.__name__} does not contain field '{key}'")

    def _get_write_target(self, key):
        return self

    def _add(self, key : str, value):
        """ Add a new attribute."""

        # Handle @property.setter
        if hasattr(self.__class__, key):
            attr = getattr(self.__class__, key)
            if isinstance(attr, property):
                attr.fset(self, value)
                return value

        # Sanity checks
        if self._frozen:
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
                return tgt._add(key, value)

        # Check if field can be None
        if value is None:
            fields_not_none = self.__class__.FIELDS_NOT_NONE or ()
            if key in fields_not_none:
                raise ValueError(f"{self.__class__.__name__} does not allow field '{key}' to be None")

        # Add to dictionary
        self._hash = None
        self._dict[key] = value
        return value

    def _remove(self, key):
        """ Remove an attribute.
        Keys may not start with '_' """

        # Sanity checks
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
        del self._dict[key]

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
        return self._get(key)

    def __setitem__(self, key : str, value):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self._add(key, value)

    def __delitem__(self, key : str):
        """ Delete an attribute using dictionary syntax """
        self._remove(key)

    def __getattr__(self, key : str):
        """ Get an attribute, redirected to the internal dictionary """
        try:
            return self._get(key)
        except KeyError:
            raise AttributeError(f"Attribute '{key}' does not exist")

    def __setattr__(self, key : str, value):
        """ Set an attribute, redirected to the internal dictionary """
        if key in self.__slots__:
            object.__setattr__(self, key, value)
        else:
            self._add(key, value)

    def __delattr__(self, key):
        """ Delete an attribute using attribute syntax """
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
            return (self.__class__.FIELDS or ()) + (self.__class__.FIELDS_NOT_NONE or ())

        return self._dict.keys()

    def items(self):
        if self._has_fixed_fields() and self.__class__.DEFAULT_TO_NONE:
            for k in self.keys():
                yield k, self[k]
            return

        return self._dict.items()

    def values(self):
        if self._has_fixed_fields() and self.__class__.DEFAULT_TO_NONE:
            for k in self.keys():
                yield self[k]
            return

        return self._dict.values()


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


    # Accessors
    def get_bool(self, attr_name : str, default=NO_DEFAULT):
        v = self._get(attr_name, default=default)
        if v is False or v == 0 or v == '0':
            return False
        elif v is True or v == 1 or v == '1':
            return True
        elif default == Namespace.NO_DEFAULT:
            raise ValueError(f"{attr_name}='{v}' is not a valid bool")
        else:
            return default

    def get_int(self, attr_name : str, default=NO_DEFAULT):
        v = self._get(attr_name, default=default)

        # Try to convert to a normal integer
        try:
            try:
                return int(v, 0)
            except TypeError:
                return int(v)
        except ValueError:
            pass

        # Return default (or fail)
        if default == Namespace.NO_DEFAULT:
            raise ValueError(f"{attr_name}='{v}' is not a valid integer")
        else:
            return default

    def get_str(self, attr_name : str, default=NO_DEFAULT):
        v = self._get(attr_name, default=default)
        if v is default:
            return v
        else:
            return str(v)

    def get_list(self, attr_name : str, default=NO_DEFAULT):
        v = self._get(attr_name, default=default)

        if v is default:
            return v
        elif isinstance(v, list):
            return v
        else:
            raise ValueError(f"{attr_name}={v} is not a valid list")


    # Freezing
    def freeze(self, recursive=True):
        """ Freezes this object, so new attributes cannot be added """
        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen') and not obj.frozen:
                    obj.freeze()
        self._frozen = True

    def unfreeze(self, recursive=True):
        """ Unfreezes this object, so new attributes can be added """
        if recursive:
            for obj in self.values():
                if hasattr(obj, 'frozen') and obj.frozen:
                    obj.unfreeze()
        self._frozen = False

    @property
    def frozen(self):
        return self._frozen
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
            self._add(k, v)


    # Logging
    @property
    def log(self):
        """ Returns a logger for the current object. If self.name is 'None', uses the class name """
        if self._log is None:
            from .log_init import getLogger
            self._log = getLogger(getattr(self, 'log_name', self), parent=self._parent)
        return self._log

    @property
    def log_name(self):
        return self._log_name
    @log_name.setter
    def log_name(self, new_name):
        if self._log_name == new_name:
            return
        if not self.__class__.FROZEN_ALLOW_SET_LOG_NAME and self._frozen:
            raise RuntimeError("Object is frozen!")
        self._log_name = new_name
        self._log = None


    # Parent
    @property
    def parent(self):
        return self._parent
    @parent.setter
    def parent(self, new_parent):
        if not self.__class__.FROZEN_ALLOW_SET_PARENT and self._frozen:
            raise RuntimeError("Object is frozen!")
        self._parent = new_parent
        self._log = None

    @property
    def hierarchy(self):
        hier = self._log_name
        if self._parent is not None:
            hier = f"{self._parent.hierarchy}.{hier}"
        return hier


    # Printing
    def __repr__(self):
        if self._parent is not None:
            nm = self.hierarchy
        else:
            nm = self._log_name
            cnm = self.__class__.__name__
            if nm != cnm:
                nm = f"{cnm}:{nm}"

        return f"<{nm} {repr(self._dict)}>"

    def __str__(self):
        return f"<{self._log_name}>"

    def repr_dict(self):
        return repr(self._dict)
