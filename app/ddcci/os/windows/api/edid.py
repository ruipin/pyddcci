# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import winreg

from ...generic.edid import Edid

from . import getLogger
log = getLogger(__name__)



#########
# Exception class
class OSEdidError(RuntimeError):
    pass



#########
# Helper methods
def edid_from_monitor_model_and_uid(model, uid):
    """
    Obtain the EDID for a Monitor given its Model and Unique ID

    :param model: The monitor's model
    :param uid: The monitor's UID

    :return: EDID bytes for the given monitor
    """
    return edid_from_monitor_registry_path(fr"SYSTEM\CurrentControlSet\Enum\DISPLAY\{model}\{uid}")


def edid_from_monitor_registry_path(reg_path, root=winreg.HKEY_LOCAL_MACHINE):
    """
    Obtain the EDID for a Monitor given its HKLM windows registry path

    :param reg_path: Registry path inside the root registry
    :param root: A winreg HKEY_* constant signifying the root registry (e.g. HKEY_LOCAL_MACHINE)
    :return: EDID for the given monitor
    """

    # NOTE: EDID can be obtained from the registry at '<monitor_path>\Device Parameters\EDID'

    # Open registry key containing the EDID
    edid_key = fr'{reg_path}\Device Parameters'
    try:
        edid_key_handle = winreg.OpenKeyEx(root, edid_key, access=winreg.KEY_READ)
    except:
        raise OSEdidError(fr"Could not open registry key '{root.__class__.__name__}\{edid_key}' for reading.")

    # Read the EDID value
    edid_subkey = 'EDID'
    try:
        edid, typ = winreg.QueryValueEx(edid_key_handle, edid_subkey)
    except:
        raise OSEdidError(fr"Could not read registry key '{root.__class__.__name__}\{edid_key}\{edid_subkey}'.")

    # Sanity check that it is binary, and we got a bytes object
    if typ != winreg.REG_BINARY:
        raise RuntimeError(fr"EDID key '{root.__class__.__name__}\{edid_key}\{edid_subkey}' does not have type REG_BINARY")
    if not isinstance(edid, bytes):
        raise RuntimeError(fr"EDID key '{root.__class__.__name__}\{edid_key}\{edid_subkey}' did not return a 'bytes' object but instead '{edid.__class__.__name__}'")

    # Close handle
    edid_key_handle.Close()

    # Decode EDID
    return Edid(edid)

