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

    # ConfigNamespace is sticky
    STICKY = True
    STICKY_DELIMITER = '.'

    # These hierarchies will not be dumped to file
    RESERVED_HIERARCHIES = ('app',)

    # Constructor
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._default = Namespace(log_name='default', parent=self)

    def _get_write_target(self, key):
        if not self._default._frozen:
            return self._default
        else:
            return self

    def _sanity_check_key(self, key, delete=False):
        super()._sanity_check_key(key)

        if self._get_write_target(key) is self._default:
            return

        if self.is_reserved_key(key):
            raise ValueError(f"key'{key}' is inside a reserved hierarchy")

    def _get_read_target(self, key):
        if key not in self._dict:
            return self._default
        else:
            return self

    def _sticky_construct_namespace(self, key):
        inst = ConfigNamespace(log_name=key, parent=self)
        if self._default.frozen:
            inst.freeze()
        return inst

    # Freezing
    def freeze(self):
        self._default.freeze()
        for k, v in self.items():
            if isinstance(v, ConfigNamespace):
                v.freeze()

    def unfreeze(self):
        self._default.unfreeze()
        for k, v in self.items():
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
    def to_dict(self, recursive=True, user=True, default=True):
        d = {}

        for k in self.keys():
            in_user    = k in self._dict
            in_default = k in self._default

            v = self._dict[k] if in_user else None
            if isinstance(v, ConfigNamespace):
                if recursive:
                    v_d = v.to_dict(recursive=True, user=user, default=default)
                    if v_d:
                        d[k] = v_d
                continue

            if not ((user and in_user) or (default and in_default)):
                continue

            if not in_user:
                v = self._default[k]
                assert(not isinstance(v, ConfigNamespace))

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
    def yaml_str(self, user=True, default=True):
        dump = self.to_dict(recursive=True, user=user, default=default)
        return yaml.dump(dump)

    def debug(self, user=True, default=True):
        dump = self.yaml_str(user=user, default=default)
        typ = 'All'  if user and default else \
              'User' if user else \
              'Default'
        self.log.debug(f"Configuration ({typ}):\n{dump}")


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
            yaml_str = self.yaml_str(user=True, default=False)
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
