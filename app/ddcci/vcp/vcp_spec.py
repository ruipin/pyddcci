# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .code import VcpCodeStorage
from app.util import CFG

########################
# Codes from the MCCS specification

VCP_SPEC = VcpCodeStorage()

_manufacturer_vcps = {}
for i in range(0xE0, 0xFF):
    _manufacturer_vcps[i] = {"name": f"Manufacturer Specific 0x{i:X}"}

VCP_SPEC.add_dictionary({
    # Preset Operations
    "Preset": {
        0x00: {
            "name": "Code Page",
            "type": "T",
            "description": "Set/get the VCP code page"
        },
        0x04: {
            "name": "Factory Defaults",
            "type": "NC",
            "description": "Restores all factory presets including luminance / contrast on a non-zero write",
            "aliases": "Restore"
        },
        0x05: {
            "name": "Factory Luminance/Contrast Defaults",
            "type": "NC",
            "description": "Restores factory defaults for luminance and constrast on a non-zero write",
            "aliases": "Restore Luminance/Contrast"
        },
        0x06: {
            "name": "Factory Geometry Defaults",
            "type": "NC",
            "description": "Restores factory defaults for geometry adjustments on a non-zero write",
            "aliases": "Restore Geometry"
        },
        0x08: {
            "name": "Factory Color Defaults",
            "type": "NC",
            "description": "Restores factory defaults for color settings on a non-zero write",
            "aliases": "Restore Color"
        },
        0x0A: {
            "name": "Factory TV Defaults",
            "type": "NC",
            "description": "Restores factory defaults for TV functions on a non-zero write",
            "aliases": "Restore TV"
        },
        0xB0: {
            "name": "Settings",
            "type": "NC",
            "description": "Store/Restore the user saved values for the current mode"
        }
    },

    # Image Adjustment
    "Image Adjustment": {
        0x0B: {
            "name": "User Color Temperature Increment",
            "type": "NC"
        },
        0x0C: {
            "name": "User Color Temperature",
            "type": "NC"
        },
        0x0E: {
            "name": "Clock",
            "type": "C",
            "description": "Video sampling clock frequency",
            "aliases": "Frequency"
        },
        0x10: {
            "name": "Luminance",
            "type": "C",
        },
        0x11: {
            "name": "Flesh Tone Enhancement",
            "type": "NC",
            "aliases": ["Flesh Tone", "Contrast Enhancement"],
            "description": "Selection of Contrast Enhancement Algorithms"
        },
        0x12: {
            "name": "Contrast",
            "type": "C",
        },
        0x13: {
            "name": "Backlight Control",
            "type": "C",
        },
        0x14: {
            "name": "Color Preset",
            "type": "NC",
            "aliases": "Color Temperature"
        },
        0x16: {
            "name": "Red Gain",
            "type": "C",
            "aliases": "Red"
        },
        0x17: {
            "name": "Color Vision Compensation",
            "type": "C"
        },
        0x18: {
            "name": "Green Gain",
            "type": "C",
            "aliases": "Green"
        },
        0x1A: {
            "name": "Blue Gain",
            "type": "C",
            "aliases": "Blue"
        },
        0x1C: {
            "name": "Focus",
            "type": "C"
        },
        0x1E: {
            "name": "Auto Focus",
            "type": "NC",
            "values": {0x00: "Disabled", 0x01: "Performing", 0x02: "Continuous"}
        },
        0x1F: {
            "name": "Auto Color Setup",
            "type": "NC",
            "values": {0x00: "Disabled", 0x01: "Performing", 0x02: "Continuous"}
        },
        0x2E: {
            "name": "Gray Scale Expansion",
            "type": "NC"
        },
        0x3E: {
            "name": "Clock Phase",
            "type": "C"
        },
        0x56: {
            "name": "Horizontal Moire",
            "type": "C"
        },
        0x58: {
            "name": "Vertical Moire",
            "type": "C"
        },
        0x59: {
            "name": "Red Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x5A: {
            "name": "Yellow Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x5B: {
            "name": "Green Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x5C: {
            "name": "Cyan Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x5D: {
            "name": "Blue Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x5E: {
            "name": "Magenta Saturation",
            "type": "C",
            "values": {0x7F: "Nominal"}
        },
        0x6B: {
            "name": "White Backlight",
            "type": "C"
        },
        0x6C: {
            "name": "Red Black Level",
            "type": "C"
        },
        0x6D: {
            "name": "Red Backlight",
            "type": "C"
        },
        0x6E: {
            "name": "Green Black Level",
            "type": "C"
        },
        0x6F: {
            "name": "Green Backlight",
            "type": "C"
        },
        0x70: {
            "name": "Blue Black Level",
            "type": "C"
        },
        0x71: {
            "name": "Blue Backlight",
            "type": "C"
        },
        0x72: {
            "name": "Gamma",
            "type": "NC"
        },
        0x73: {
            "name": "LUT Size",
            "type": "T"
        },
        0x74: {
            "name": "Single Point LUT Operation",
            "type": "T"
        },
        0x75: {
            "name": "Block LUT Operation",
            "type": "T"
        },
        0x7C: {
            "name": "Zoom",
            "type": "C",
            "description": "Zoom function",
            "aliases": "Adjust Zoom"
        },
        0x87: {
            "name": "Sharpness",
            "type": "C"
        },
        0x88: {
            "name": "Velocity Scan Modulation",
            "type": "C"
        },
        0x8A: {
            "name": "Saturation",
            "type": "C",
            "aliases": "Color Saturation"
        },
        0x8C: {
            "name": "TV Sharpness",
            "type": "C",
            "description": "Sharpness control for TV inputs"
        },
        0x8E: {
            "name": "TV Contrast",
            "type": "C",
            "description": "Contrast control for TV inputs"
        },
        0x90: {
            "name": "Hue",
            "type": "C",
            "aliases": "Tint"
        },
        0x92: {
            "name": "TV Black Level",
            "type": "C",
            "description": "Black Level control for TV inputs"
        },
        0x9A: {
            "name": "Window Background",
            "type": "C",
            "description": "Contrast ratio between area of the window and the rest of the desktop"
        },
        0x9B: {
            "name": "Red Hue",
            "type": "C"
        },
        0x9C: {
            "name": "Yellow Hue",
            "type": "C"
        },
        0x9D: {
            "name": "Green Hue",
            "type": "C"
        },
        0x9E: {
            "name": "Cyan Hue",
            "type": "C"
        },
        0x9F: {
            "name": "Blue Hue",
            "type": "C"
        },
        0xA0: {
            "name": "Magenta Hue",
            "type": "C"
        },
        0xA2: {
            "name": "Auto Setup",
            "type": "NC",
            "values": {0x01: "Off", 0x02: "On"}
        },
        0xA4: {
            "name": "Window Mask Control",
            "type": "T"
        },
        0xA5: {
            "name": "Window Select",
            "type": "C"
        },
        0xA6: {
            "name": "Window Size",
            "type": "C"
        },
        0xA7: {
            "name": "Window Transparency",
            "type": "C"
        },
        0xAA: {
            "name": "Screen Orientation",
            "type": "NC",
            "aliases": "Orientation",
            "values": {0x01: "0 degrees", 0x02: "90 degrees", 0x03: "180 degrees", 0x04: "270 degrees", 0xFF: "Not Applicable"}
        },
        0xD4: {
            "name": "Stereo Video Mode",
            "type": "NC",
            "aliases": "Stereo"
        },
        0xDC: {
            "name": "Display Application",
            "type": "NC",
            "aliases": ["Application", "Preset"],
            "values": {
                0x00: ["Stand", "Default"], 0x01: "Productivity", 0x02: "Mixed", 0x03: ["Movie", "Cinema"], 0x04: "User", 0x05: ["Games", "Gaming"],
                0x06: "Sports", 0x07: "Professional", 0x08: "Standard", 0x09: "Low power", 0x0A: "Demonstration", 0xF0: "Dynamic Contrast"}
        }
    },


    # Display Control
    "Display Control": {
        0xB4: {
            "name": "Source Timing Mode",
            "type": "T",
            "aliases": "Timing"
        },
        0xCA: {
            "name": "OSD / Button Control",
            "type": "NC",
            "aliases": ["OSD Control", "Button Control"]
        },
        0xAC: {
            "name": "Horizontal Frequency",
            "type": "C"
        },
        0xAE: {
            "name": "Vertical Frequency",
            "type": "C"
        },
        0xB5: {
            "name": "Source Color Coding",
            "type": "NC"
        },
        0xC0: {
            "name": "Display Usage Time",
            "type": "C",
            "aliases": ["Power On Time", "Uptime"],
            "description": "Hours of active power on time"
        },
        0xC8: {
            "name": "Display Controller ID",
            "type": "NC"
        },
        0xC9: {
            "name": "Display Firmware Level",
            "type": "C"
        },
        0xCC: {
            "name": "OSD Language",
            "type": "NC"
        },
        0xD6: {
            "name": "Power Mode",
            "type": "NC",
            "aliases": "Power",
            "values": {0x01: "On", 0x02: "Standby", 0x03: "Suspend", 0x04: "Off", 0x05: "Hard Off"}
        },
        0xDB: {
            "name": "Image Mode",
            "type": "NC",
            "values": {0x01: "Full", 0x02: "Zoom", 0x03: "Squeeze", 0x04: "Variable"}
        },
        0xDF: {
            "name": "VCP Version",
            "type": "NC",
        }
    },


    # Geometry
    "Geometry": {
        0x20: {
            "name": "Horizontal Position",
            "aliases": "Horizontal Phase",
            "type": "C"
        },
        0x22: {
            "name": "Horizontal Size",
            "type": "C"
        },
        0x24: {
            "name": "Horizontal Pincushion",
            "type": "C"
        },
        0x26: {
            "name": "Horizontal Pincushion Balance",
            "type": "C"
        },
        0x28: {
            "name": "Horizontal Convergence R/B",
            "type": "C"
        },
        0x29: {
            "name": "Horizontal Convergence M/G",
            "type": "C"
        },
        0x2A: {
            "name": "Horizontal Linearity",
            "type": "C"
        },
        0x2C: {
            "name": "Horizontal Linearity Balance",
            "type": "C"
        },
        0x30: {
            "name": "Vertical Position",
            "aliases": "Vertical Phase",
            "type": "C"
        },
        0x32: {
            "name": "Vertical Size",
            "type": "C"
        },
        0x34: {
            "name": "Vertical Pincushion",
            "type": "C"
        },
        0x36: {
            "name": "Vertical Pincushion Balance",
            "type": "C"
        },
        0x38: {
            "name": "Vertical Convergence R/B",
            "type": "C"
        },
        0x39: {
            "name": "Vertical Convergence M/G",
            "type": "C"
        },
        0x3A: {
            "name": "Vertical Linearity",
            "type": "C"
        },
        0x3C: {
            "name": "Vertical Linearity Balance",
            "type": "C"
        },
        0x40: {
            "name": "Horizontal Parallelogram",
            "type": "C"
        },
        0x41: {
            "name": "Vertical Parallelogram",
            "type": "C"
        },
        0x42: {
            "name": "Horizontal Keystone",
            "type": "C"
        },
        0x43: {
            "name": "Vertical Keystone",
            "type": "C"
        },
        0x44: {
            "name": "Rotation",
            "type": "C"
        },
        0x46: {
            "name": "Top Corner Flare",
            "type": "C"
        },
        0x48: {
            "name": "Top Corner Hook",
            "type": "C"
        },
        0x4A: {
            "name": "Bottom Corner Flare",
            "type": "C"
        },
        0x4C: {
            "name": "Bottom Corner Hook",
            "type": "C"
        },
        0x82: {
            "name": "Horizontal Mirror",
            "aliases": "Horizontal Flip",
            "type": "NC",
            "values": {0x00: "Normal", 0x11: ["Mirrored", "Flipped"]}
        },
        0x84: {
            "name": "Vertical Mirror",
            "aliases": "Vertical Flip",
            "type": "NC",
            "values": {0x00: "Normal", 0x11: ["Mirrored", "Flipped"]}
        },
        0x86: {
            "name": "Display Scaling",
            "aliases": "Scaling",
            "type": "NC"
        },
        0x95: {
            "name": "Window Position TL_X",
            "aliases": "TL_X",
            "type": "C"
        },
        0x96: {
            "name": "Window Position TL_Y",
            "aliases": "TL_Y",
            "type": "C"
        },
        0x97: {
            "name": "Window Position BR_X",
            "aliases": "BR_X",
            "type": "C"
        },
        0x98: {
            "name": "Window Position BR_Y",
            "aliases": "BR_Y",
            "type": "C"
        },
        0xDA: {
            "name": "Scan Mode",
            "aliases": "Scan",
            "type": "NC",
            "values": {0x00: "Normal", 0x01: "Underscan", 0x02: "Overscan"}
        }
    },


    # Miscellaneous
    "Miscellaneous": {
        0x54: {
            "name": "Performance Preservation",
            "description": "Control up to 16 features aimed at maintaining the performance of the display",
            "type": "NC"
        },
        0x60: {
            "name": "Input Select",
            "aliases": "Input",
            "type": "NC",
            "values": {
                0x01: ["RGB 1", "Analog 1"], 0x02: ["RGB 2", "Analog 2"],
                0x03: ["DVI 1", "Digital 1"], 0x04: ["DVI 2", "Digital 2"],
                0x05: "Composite 1", 0x06: "Composite 2",
                0x07: "S-Video 1", 0x08: "S-Video 2",
                0x09: "Tuner 1", 0x0A: "Tuner 2", 0x0B: "Tuner 3",
                0x0C: "Component 1", 0x0D: "Component 2", 0x0E: "Component 3",
                0x0F: ["DP 1", "DisplayPort 1"], 0x10: ["DP 2", "DisplayPort 2"],
                0x11: ["HDMI 1", "Digital 3"], 0x12: ["HDMI 2", "Digital 4"]
            }
        },
        0x66: {
            "name": "Ambient Light Sensor",
            "type": "NC"
        },
        0x76: {
            "name": "Remote Procedure Call",
            "aliases": "RPC",
            "type": "T"
        },
        0x78: {
            "name": "Display Identification Data Operation",
            "type": "T"
        },
        0x8B: {
            "name": "TV Channel Up/Down",
            "aliases": "TV Channel",
            "type": "NC",
            "values": {0x01: ["Up", "Increment"], 0x02: ["Down", "Decrement"]}
        },
        0xB2: {
            "name": "Flat Panel Sub-Pixel Layout",
            "aliases": ["Sub-Pixel Layout", "SPL"],
            "type": "NC",
            "values": {0x00: "Undefined", 0x01: "RGB vertical", 0x02: "RGB horizontal", 0x03: "BGR vertical", 0x04: "BGR horizontal", 0x05: "Quad RGBG",
                       0x06: "Quad BGRG", 0x07: ["Delta", "Triad"], 0x08: "Mosaic"}
        },
        0xB6: {
            "name": "Display Technology Type",
            "aliases": "Technology",
            "type": "NC"
        },
        0xC2: {
            "name": "Display Descriptor Length",
            "type": "C"
        },
        0xC3: {
            "name": "Transmit Display Descriptor",
            "type": "T"
        },
        0xC4: {
            "name": "Enable Display of Display Descriptor",
            "type": "NC"
        },
        0xC6: {
            "name": "Application Enable Key",
            "type": "NC"
        },
        0xC7: {
            "name": "Display Enable Key",
            "type": "NC"
        },
        0xCD: {
            "name": "Host Status Indicators",
            "type": "NC"
        },
        0xCE: {
            "name": "Auxiliary Display Size",
            "type": "NC"
        },
        0xCF: {
            "name": "Auxiliary Display Data",
            "type": "T"
        },
        0xD0: {
            "name": "Output Select",
            "type": "NC"
        },
        0xD2: {
            "name": "Asset Tag",
            "type": "T"
        },
        0xD7: {
            "name": "Auxiliary Power Output",
            "type": "NC"
        },
        0xDE: {
            "name": "Scratch Pad",
            "type": "NC"
        }
    },


    # Audio
    "Audio": {
        0x62: {
            "name": "Speaker Volume",
            "aliases": "Volume",
            "type": "NC"
        },
        0x63: {
            "name": "Speaker Select",
            "type": "NC"
        },
        0x64: {
            "name": "Microphone Volume",
            "type": "C"
        },
        0x65: {
            "name": "Jack Connection Status",
            "type": "NC"
        },
        0x8D: {
            "name": "Audio Mute / Screen Blank",
            "aliases": ["Audio Mute", "Mute", "Screen Blank", "Blank"],
            "type": "NC"
        },
        0x8F: {
            "name": "Audio Treble",
            "aliases": "Treble",
            "type": "NC"
        },
        0x91: {
            "name": "Audio Bass",
            "aliases": "Bass",
            "type": "NC"
        },
        0x93: {
            "name": "Audio Balance L/R",
            "aliases": "Audio Balance",
            "type": "NC"
        },
        0x94: {
            "name": "Audio Processor Mode",
            "type": "NC"
        }
    },


    # DPVL
    "DPVL": {
        0xB7: {
            "name": "Monitor Status",
            "type": "NC"
        },
        0xB8: {
            "name": "Packet Count",
            "type": "C"
        },
        0xB9: {
            "name": "Monitor X Origin",
            "type": "C"
        },
        0xBA: {
            "name": "Monitor Y Origin",
            "type": "C"
        },
        0xBB: {
            "name": "Header Error Count",
            "type": "C"
        },
        0xBC: {
            "name": "Body CRC Error Count",
            "type": "C"
        },
        0xBD: {
            "name": "Client ID",
            "type": "C"
        },
        0xBE: {
            "name": "Link Control",
            "type": "NC"
        }
    },


    # Manufacturer Specific
    "Manufacturer": _manufacturer_vcps
})


custom_codes = CFG.vcp.custom_codes
if custom_codes is not None:
    VCP_SPEC.deserialize(custom_codes)