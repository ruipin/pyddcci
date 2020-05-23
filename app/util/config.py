# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import os
import yaml
from ordered_set import OrderedSet

from . import Namespace
from . import args as ARGS
from . import version as VERSION



##########
# Config Namespace Class
class ConfigNamespace(Namespace):
    """ Storage class for configuration settings """

    # Python does not inherit __slots__ automatically
    __slots__ = set.union({'_default'}, Namespace.__slots__)

    # These hierarchies will not be dumped to file
    RESERVED_HIERARCHIES = ('app',)

    # Constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._default = Namespace(log_name='default', parent=self)

    def _get(self, key, default=Namespace.NO_DEFAULT):
        if key in self._dict:
            return super()._get(key, default=default)

        return self._default.get(key, default=default)

    def _add(self, key, value, delete=False):
        split_key = key.split('.', 1)
        key = split_key[0]

        if len(split_key) > 1:
            new_value = ConfigNamespace(log_name=key, parent=self)
            new_value[split_key[1]] = value
            value = new_value
        elif isinstance(value, dict):
            new_value = ConfigNamespace(log_name=key, parent=self)
            new_value.merge(value)
            value = new_value

        if not self._default._frozen:
            self._default._add(key, value, delete=delete)
        else:
            if key in self._default:
                def_val = self._default[key]
                if isinstance(def_val, ConfigNamespace) and delete is False and not isinstance(value, ConfigNamespace):
                    raise ValueError(f"key='{key}' must be a dictionary, or 'delete' must be True")

            if self.is_reserved_key(key):
                raise ValueError(f"key'{key}' is inside a reserved hierarchy")

            super()._add(key, value, delete=delete)


    # Freezing
    def freeze(self):
        self._default.freeze()
        for k, v in self._default.items():
            if isinstance(v, ConfigNamespace):
                v.freeze()

    def unfreeze(self):
        self._default.unfreeze()
        for k, v in self._default.items():
            if isinstance(v, ConfigNamespace):
                v.unfreeze()


    # Iteration
    def __iter__(self):
        """ Returns an iterator to the internal dictionary """
        for k in self.keys():
            yield k

    def __len__(self):
        """ Returns the length of the internal dictionary """
        return len(self.keys())

    def keys(self):
        return OrderedSet.union(self._default.keys(), self._dict.keys())

    def items(self):
        for k in self.keys():
            yield k, self.get(k)

    def values(self):
        return self._dict.values()


    # Utilities
    def all_to_dict(self):
        d = {}
        for k, v in self.items():
            if isinstance(v, ConfigNamespace):
                v = v.all_to_dict()
            d[k] = v
        return d

    def user_to_dict(self):
        d = {}

        for k, v in self._dict.items():
            if self.is_reserved_key(k):
                continue

            if isinstance(v, ConfigNamespace):
                v = v.user_to_dict()

            d[k] = v

        return d

    def is_reserved_key(self, key):
        self_hier = f"{self.hierarchy}.{key}"

        for v in self.__class__.RESERVED_HIERARCHIES:
            if self_hier.startswith(f"{CONFIG.log_name}.{v}.") or self_hier == v:
                return True

        return False


class MasterConfigNamespace(ConfigNamespace):
    """ Storage class for configuration settings """

    # Python does not inherit __slots__ automatically
    __slots__ = ConfigNamespace.__slots__


    # Constants
    USER_CONFIG_FILE = os.path.join(ARGS.HOME, 'data', 'config.yaml')
    DEFAULT_CONFIG_FILE = os.path.join(ARGS.HOME, 'data', 'config.default.yaml')


    # Utilities
    def yaml_str(self, user_only=False):
        mthd = self.user_to_dict if user_only else self.all_to_dict
        return yaml.dump(mthd())

    def debug(self, user_only=False):
        dump = self.yaml_str(user_only=user_only)
        self.log.debug(f"Configuration{' (User)' if user_only else ' (All)'}:\n{dump}")


    # Load/Save
    def load_path(self, file_path):
        with open(file_path, 'r') as file:
            yaml_d = yaml.load(file, Loader=yaml.FullLoader)

        if yaml_d is not None:
            self.merge(yaml_d)

    def load(self):
        if self.frozen:
            self.unfreeze()

        # Load default file
        self.load_path(self.__class__.DEFAULT_CONFIG_FILE)

        # Add command-line arguments
        for k in vars(ARGS.ARGS):
            v = getattr(ARGS, k)
            if v is not None:
                self[k] = getattr(ARGS, k)

        # Add app information
        self['app'] = {
            'name': ARGS.NAME,
            'version': {
                'revision': VERSION.GIT_REVISION,
                'version': VERSION.VERSION,
                'full': VERSION.VERSION_STRING
            },
            'dirs': {
                'home': ARGS.HOME,
            }
        }

        # Freeze all values so far - they'll be the default values
        self.freeze()

        # Load user config if it exists
        user_path = self.__class__.USER_CONFIG_FILE
        if os.path.isfile(user_path):
            self.load_path(user_path)


    def save(self):
        self.log.info("Saving user configuration...")
        with open(self.__class__.USER_CONFIG_FILE, 'w') as file:
            yaml_str = self.yaml_str(user_only=True)
            file.write(yaml_str)

# Initialize
CONFIG = MasterConfigNamespace("config")
CONFIG.load()



####################
# Helpers
def __getattr__(name):
    """ Get an attribute using attribute syntax obj.name """

    # Handle methods first
    if hasattr(CONFIG, name):
        mthd = getattr(CONFIG, name)
        if callable(mthd):
            return mthd

    # Do a normal namespace access
    return CONFIG.get(name)

def __getitem__(key):
    """ Get an attribute using dictionary syntax obj[key] """
    return CONFIG.get(key)


# Cleanup
del ARGS
del VERSION
