# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from . import shorten_name


class NamedMixin(object):
    """
    Mixin that adds a name to a class instance.

    Provides instance_name and related properties for identification, logging, and display purposes.
    Used for configuration, logging, and user-facing objects in pyddcci.
    """
    def __init__(self, *args, instance_name=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.__name = instance_name

    @classmethod
    def class_short_name(cls) -> str:
        return shorten_name(cls.__name__)

    # Logging
    def _set_instance_name(self, new_name : str) -> None:
        self.__name = new_name

    @property
    def instance_name(self) -> str:
        return self.__name or self.__class__.__name__
    @instance_name.setter
    def instance_name(self, new_name : str) -> None:
        self._set_instance_name(new_name)

    @property
    def instance_short_name(self) -> str:
        return shorten_name(self.instance_name)


    # Printing
    @property
    def __repr_name(self) -> str:
        nm  = self.instance_name
        cnm = self.__class__.__name__

        if cnm in nm:
            return nm
        else:
            return f"{cnm}:{nm}"

    def __repr__(self) -> str:
        return f"<{self.__repr_name}>"

    @property
    def __str_name(self) -> str:
        nm = self.instance_name
        cnm = self.__class__.__name__

        if nm == cnm:
            return nm
        else:
            return f"{self.__class__.class_short_name()} {nm}"

    def __str__(self) -> str:
        return f"<{self.__str_name}>"