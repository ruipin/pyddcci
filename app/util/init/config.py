# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import os
import oyaml as yaml
from ordered_set import OrderedSet

from . import version, args
from .. import NamespaceMap, LoggableHierarchicalNamedMixin


##########
# Config Namespace Class
class ConfigMap(NamespaceMap, LoggableHierarchicalNamedMixin):
    """
    Storage class for configuration settings.
    Supports sticky namespaces, reserved/raw hierarchies, and merging from YAML.
    """

    # ConfigNamespace is sticky
    NAMESPACE__STICKY = True
    NAMESPACE__STICKY__DELIMITER = '.'

    # These hierarchies will not be dumped to file
    RESERVED_HIERARCHIES = ('app',)

    # These hierarchies will be stored raw
    RAW_HIERARCHIES = ('vcp.custom_codes',)

    def __init__(self, instance_name, *args, **kwargs):
        """
        Initialize the ConfigMap with an instance name and optional arguments.

        Args:
            instance_name (str): The name for this config map.
            *args: Additional positional arguments.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(*args, instance_name=instance_name, **kwargs)

        self._default = NamespaceMap()

    def _get_write_target(self, key):
        """
        Get the write target for a given key (default or self).

        Args:
            key (str): The key to check.

        Returns:
            NamespaceMap: The write target.
        """
        if not self._default.frozen_schema:
            return self._default
        else:
            return self

    def _sanity_check_key(self, key, delete=False):
        """
        Check if a key is valid and not reserved.

        Args:
            key (str): The key to check.
            delete (bool): If True, check for deletion.

        Raises:
            ValueError: If the key is reserved.
        """
        super()._sanity_check_key(key)

        if self._get_write_target(key) is self.get('_default', None):
            return

        if self.is_reserved_key(key):
            raise ValueError(f"key'{key}' is inside a reserved hierarchy")

    def _get_read_target(self, key):
        """
        Get the read target for a given key (default or self).

        Args:
            key (str): The key to check.

        Returns:
            NamespaceMap: The read target.
        """
        if key not in self.__dict__:
            return self._default
        else:
            return self

    @classmethod
    def _sticky_construct_class(cls) -> type:
        """
        Return the class to use for sticky construction.

        Returns:
            type: The class type.
        """
        return ConfigMap

    def freeze_default(self):
        """
        Freeze the default config map and all contained ConfigMaps.
        """
        self._default.freeze_map()
        for k, v in self.items():
            if isinstance(v, ConfigMap):
                v.freeze_map()

    def __iter__(self):
        """
        Returns an iterator to the internal dictionary.

        Returns:
            iterator: An iterator over the keys.
        """
        for k in self.keys():
            yield k

    def __len__(self):
        """
        Returns the length of the internal dictionary.

        Returns:
            int: The number of keys.
        """
        return len(self.keys())

    def keys(self):
        """
        Get all keys in the config map.

        Returns:
            OrderedSet: A set of all keys.
        """
        return OrderedSet.union(self._default.keys(), self.__dict__.keys())

    def items(self):
        """
        Get all items in the config map.

        Returns:
            iterator: An iterator over key-value pairs.
        """
        for k in self.keys():
            yield k, self.get(k)

    def values(self):
        """
        Get all values in the config map.

        Returns:
            list: A list of all values.
        """
        return self._dict.values()

    def asdict(self, recursive=True, user=True, default=True):
        """
        Convert the config map to a dictionary, optionally recursively.

        Args:
            recursive (bool): If True, convert recursively.
            user (bool): Include user values.
            default (bool): Include default values.

        Returns:
            dict: The dictionary representation.
        """
        d = {}

        for k in self.keys():
            in_user    = k in self.__dict__
            in_default = k in self._default

            v = self.__dict__[k] if in_user else None
            if isinstance(v, ConfigMap):
                if recursive:
                    v_d = v.asdict(recursive=True, user=user, default=default)
                    if v_d:
                        d[k] = v_d
                continue

            if not ((user and in_user) or (default and in_default)):
                continue

            if not in_user:
                v = self._default[k]
                assert(not isinstance(v, ConfigMap))

            d[k] = v

        return d

    def is_reserved_key(self, key : str) -> bool:
        """
        Check if a key is inside a reserved hierarchy.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if reserved, False otherwise.
        """
        key_hier = f"{self.instance_hierarchy}.{key}"
        key_hier = key_hier.split('.', 1)[1]

        for v in self.__class__.RESERVED_HIERARCHIES:
            if key_hier.startswith(f"{v}.") or key_hier == v:
                return True

        return False

    def _sticky_ignore_key(self, key : str) -> bool:
        """
        Whether a key should be ignored for sticky construction.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if this key should be ignored, False otherwise.
        """
        key_hier = f"{self.instance_hierarchy}.{key}"
        key_hier = key_hier.split('.', 1)[1]

        for v in self.__class__.RAW_HIERARCHIES:
            if key_hier.startswith(f"{v}.") or key_hier == v:
                return True

        return False


class MasterConfigMap(ConfigMap):
    """
    Storage class for configuration settings, with user and default config file support.
    """

    # Constants
    USER_CONFIG_FILE = os.path.join(args.HOME, 'data', 'config.yaml')
    DEFAULT_CONFIG_FILE = os.path.join(args.HOME, 'data', 'config.default.yaml')

    def yaml_str(self, user=True, default=True):
        """
        Get the YAML string representation of the config.

        Args:
            user (bool): Include user values.
            default (bool): Include default values.

        Returns:
            str: The YAML string.
        """
        dump = self.asdict(recursive=True, user=user, default=default)
        return yaml.dump(dump)

    def debug(self, user=True, default=True):
        """
        Log the YAML string representation of the config for debugging.

        Args:
            user (bool): Include user values.
            default (bool): Include default values.
        """
        dump = self.yaml_str(user=user, default=default)
        typ = 'All'  if user and default else \
              'User' if user else \
              'Default'
        self.log.debug(f"Configuration ({typ}):\n{dump}")

    def load_path(self, file_path):
        """
        Load config from a YAML file at the given path.

        Args:
            file_path (str): Path to the YAML file.
        """
        if not os.path.exists(file_path):
            return

        with open(file_path, 'r') as file:
            yaml_d = yaml.load(file, Loader=yaml.FullLoader)

        if yaml_d is not None:
            self.merge(yaml_d)

    def load(self):
        """
        Load the default and user config files, merge CLI args, and freeze defaults.
        """
        # Load default file
        self.load_path(self.__class__.DEFAULT_CONFIG_FILE)

        # Initialize app namespace
        self['app'] = {}

        # Add command-line arguments
        for k in vars(args.ARGS):
            v = getattr(args, k)
            if v is not None:
                self[k] = v

        # Add app information
        self['app'].merge({
            'name': args.NAME,
            'version': {
                'revision': version.GIT_REVISION,
                'version': version.VERSION,
                'full': version.VERSION_STRING
            },
            'dirs': {
                'home': args.HOME,
                'data': os.path.join(args.HOME, 'data')
            },
            'test': args.UNIT_TEST
        })

        # Freeze all values so far - they'll be the default values
        self.freeze_default()

        # Load user config if it exists
        user_path = self.__class__.USER_CONFIG_FILE
        if os.path.isfile(user_path):
            self.load_path(user_path)

    def save(self):
        """
        Save the user configuration to the user configuration file.
        """
        self.log.debug("Saving user configuration...")
        assert not CONFIG.app.test
        with open(self.__class__.USER_CONFIG_FILE, 'w') as file:
            yaml_str = self.yaml_str(user=True, default=False)
            file.write(yaml_str)

# Initialize
CONFIG = MasterConfigMap("config")
CONFIG.load()


####################
# Helpers
def __getattr__(name):
    """
    Get a config attribute using attribute syntax obj.name.

    Args:
        name (str): The attribute name.

    Returns:
        The attribute value or method.
    """
    # Handle methods first
    if hasattr(CONFIG, name):
        mthd = getattr(CONFIG, name)
        if callable(mthd):
            return mthd

    # Do a normal namespace access
    return CONFIG.get(name)

def __getitem__(key):
    """
    Get a config attribute using dictionary syntax obj[key].

    Args:
        key (str): The attribute name.

    Returns:
        The attribute value.
    """
    return CONFIG.get(key)


# Cleanup
del args
del version
