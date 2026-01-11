#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# constants.py from https://github.com/snstac/aircot
#
# Copyright Sensors & Signals LLC https://www.snstac.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

"""AirCOT Constants.

This module contains configuration constants for aircraft classification including:
- Logging configuration
- CoT (Cursor on Target) default values
- ICAO hex address ranges for country/affiliation classification
- Known airline identifiers
"""

import logging
import os
from pathlib import Path

LOG_LEVEL: int = logging.INFO
LOG_FORMAT: logging.Formatter = logging.Formatter(
    ("%(asctime)s aircot %(levelname)s - %(message)s")
)

if bool(os.environ.get("DEBUG")):
    LOG_LEVEL = logging.DEBUG
    LOG_FORMAT = logging.Formatter(
        (
            "%(asctime)s aircot %(levelname)s %(name)s.%(funcName)s:%(lineno)d - "
            "%(message)s"
        )
    )
    logging.debug("aircot Debugging Enabled via DEBUG Environment Variable.")

DEFAULT_COT_STALE: int = 120
DEFAULT_COT_VAL: str = "9999999.0"

W3C_XML_DATETIME: str = "%Y-%m-%dT%H:%M:%S.%fZ"
ISO_8601_UTC: str = "%Y-%m-%dT%H:%M:%SZ"

DEFAULT_ADSB_ID_DB: str = "cotdb_indexed.json"

# FIXME: Maybe transition this to a text file?
#  3LD identifiers change rapidly, not major airlines, but there are hundreds of
#  these world wide...
DOMESTIC_US_AIRLINES: list = [
    "AAL",  # American Airlines
    "UAL",  # United Airlines
    "FDX",  # FedEx
    "UPS",  # UPS Airlines
    "SWA",  # Southwest Airlines
    "DAL",  # Delta Air Lines
    "JBU",  # JetBlue Airways
    "ASA",  # Alaska Airlines
    "SKW",  # SkyWest Airlines
    "FFT",  # Frontier Airlines
    "NKS",  # Spirit Airlines
    "AAY",  # Allegiant Air
    "SWQ",  # Swift Air
    "FLG",  # Endeavor Air
    "CPZ",  # Compass Airlines
    "RPA",  # Republic Airways
    "ENY",  # Envoy Air
    "GJS",  # GoJet Airlines
    "JIA",  # PSA Airlines
    "PDT",  # Piedmont Airlines
    "CHQ",  # Chautauqua Airlines
    "EJA",  # NetJets
    "CSQ",  # IBC Airways
    "XOJ",  # XOJET
]

DEFAULT_HEX_RANGES: dict = {
    # Known 'friendly' ICAO hex ranges for civilian and military aircraft
    # Key format: "<COUNTRY>-<AFFILIATION>" where affiliation is CIV or MIL
    "US-CIV": {"start": 0xA00000, "end": 0xADF7C7},
    "US-MIL": {"start": 0xADF7C8, "end": 0xAFFFFF},
    "CAN-CIV": {"start": 0xC00000, "end": 0xC0CDF8},
    "CAN-MIL": {"start": 0xC0CDF9, "end": 0xC3FFFF},
    "NZ-CIV": {"start": 0xC80000, "end": 0xC87DFF},
    "NZ-gnd": {
        "start": 0xC87E00,
        "end": 0xC87EFF,
    },  # reserved for ground vehicle transponders
    "NZ-MIL": {"start": 0xC87F00, "end": 0xC87FFF},
    "AUS-CIV": {"start": 0x7C0000, "end": 0x7FFFFF},
    "AUS-MIL": {"start": 0x7CF800, "end": 0x7CFAFF},
    "UK-CIV": {"start": 0x400000, "end": 0x43FFFF},
    "UK-MIL": {"start": 0x43C000, "end": 0x43CFFF},
}

# Use absolute path relative to this module's location
DEFAULT_COUNTRIES_FILE: str = str(Path(__file__).parent / "data" / "countries.json")
DEFAULT_COTDB_FILE: str = str(Path(__file__).parent / "data" / "cotdb.json")