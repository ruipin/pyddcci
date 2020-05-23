# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import functools
import operator


class Namespace(object):
    """
    Class implementing a namespace that can be accessed like a dictionary or using attributes

    Classes inheriting should make sure they inherit __slots__, e.g.
    >>> __slots__ = Namespace.__slots__

    To add new slots, make sure to also inherit the existing slots, e.g.
    >>> __slots__ = set.union({'_banana'}, Namespace.__slots__)
    """

    # Tell Python to omit the built-in __dict__
    __slots__ = {'_dict', '_hash', '_log_name', '_frozen', '_parent', '_log'}


    # Constructor
    def __init__(self, log_name : str, parent=None, frozen=False):
        self._hash     = None
        self._log_name = log_name
        self._log      = None
        self._frozen   = False
        self._parent   = parent
        self._dict     = {}
        self._frozen   = frozen


    # Dictionary behaviour
    def _add(self, key : str, value, delete=False):
        """ Add a new attribute.
        Keys may not start with '_' """
        if self._frozen:
            raise TypeError(f"{repr(self)} is frozen")
        if not key:
            raise ValueError(f"key must be defined")
        elif key[0] == '_':
            raise ValueError(f"key='{key}' may not start with '_'")
        elif f"_{key}" in self.__class__.__slots__:
            raise ValueError(f"key='{key}' is reserved")

        # Store in _dict
        self._hash = None
        if delete:
            del self._dict[key]
        else:
            self._dict[key] = value


    NO_DEFAULT = object()
    def _get(self, key : str, default=NO_DEFAULT):
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
        """ Delete an attribute using 'del <attr>' syntax """
        self._add(key, None, delete=True)

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
        return self._dict.keys()

    def items(self):
        return self._dict.items()

    def values(self):
        return self._dict.values()


    # Comparison
    def __eq__(self, other):
        return self is other
        # return hash(self) == hash(other)

    def __ne__(self, other):
        return self is not other
        # return hash(self) != hash(other)

    def __hash__(self):
        """ Calculates a hash of the internal dictionary """
        if self._hash is None:
            hashes = map(hash, self.items())
            self._hash = functools.reduce(operator.xor, hashes, 0)
        return self._hash


    # Freezing
    def freeze(self):
        """ Freezes this object, so new attributes cannot be added """
        if self._frozen:
            raise RuntimeError('Already frozen')
        self._frozen = True

    def unfreeze(self):
        """ Unfreezes this object, so new attributes can be added """
        if not self._frozen:
            raise RuntimeError('Already unfrozen')
        self._frozen = False


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

    # Utilities
    def to_dict(self):
        return dict(self._dict)

    def merge(self, d):
        for k, v in d.items():
            self._add(k, v)

    # Properties
    @property
    def log(self):
        """ Returns a logger for the current object. If self.name is 'None', uses the class name """
        if self._log is None:
            from .log_init import getLogger
            self._log = getLogger(getattr(self, 'log_name', self), parent=self._parent)
        return self._log

    @property
    def frozen(self):
        return self._frozen

    @property
    def hierarchy(self):
        hier = self._log_name
        if self._parent is not None:
            hier = f"{self._parent.hierarchy}.f{hier}"
        return hier

    @property
    def log_name(self):
        return self._log_name

    # Printing
    def __repr__(self):
        return "<%s.%s %r>" % (self.__class__.__name__, self._log_name, self._dict)
    def __str__(self):
        return str(self._dict)
    def repr_dict(self):
        return repr(self._dict)
