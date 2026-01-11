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

"""AirCOT Functions."""

import bisect
import csv
import json
import logging

from typing import Optional, Union, Tuple

from aircot.constants import DEFAULT_COUNTRIES_FILE, DEFAULT_HEX_RANGES, DOMESTIC_US_AIRLINES, DEFAULT_COT_VAL

__author__ = "Greg Albrecht <gba@snstac.com>"
__copyright__ = "Copyright Sensors & Signals LLC https://www.snstac.com"
__license__ = "Apache License, Version 2.0"


# Load ICAO country ranges from JSON/CSV file and pre-compute sorted structures once
try:
    with open(DEFAULT_COUNTRIES_FILE, encoding="UTF-8") as f:
        # Try JSON first, fall back to CSV if that fails
        try:
            data = json.load(f)
            if isinstance(data, list):
                # Convert hex strings to integers
                _ICAO_SORTED = sorted(
                    ({"start": int(row["start"], 16), "end": int(row["end"], 16), "country": row["country"]} 
                     for row in data),
                    key=lambda x: x["start"]
                )
            else:
                _ICAO_SORTED = []
        except json.JSONDecodeError:
            # Fall back to CSV format
            f.seek(0)
            reader = csv.DictReader(f)
            _ICAO_SORTED = sorted(
                ({"start": int(row["start"], 16), "end": int(row["end"], 16), "country": row["country"]} 
                 for row in reader),
                key=lambda x: x["start"]
            )
    _ICAO_STARTS = [r["start"] for r in _ICAO_SORTED]
except FileNotFoundError:
    logging.warning(f"Countries file not found: {DEFAULT_COUNTRIES_FILE}. Country lookup will be unavailable.")
    _ICAO_SORTED = []
    _ICAO_STARTS = []
except Exception as e:
    logging.error(f"Error loading countries file: {e}. Country lookup will be unavailable.")
    _ICAO_SORTED = []
    _ICAO_STARTS = []


# Compute once at module initialization
_CIV_RANGES = [k for k in DEFAULT_HEX_RANGES if "-CIV" in k]
_MIL_RANGES = [k for k in DEFAULT_HEX_RANGES if "-MIL" in k]
_RANGE_CACHE = {"CIV": _CIV_RANGES, "MIL": _MIL_RANGES}


def lookup_country(icao: int) -> Optional[str]:
    """O(log n) country lookup using binary search."""
    idx = bisect.bisect_right(_ICAO_STARTS, icao) - 1
    if idx >= 0:
        entry = _ICAO_SORTED[idx]
        if entry["start"] <= icao <= entry["end"]:
            return entry["country"]
    return None


# TODO: Pull this out into a custom csv or txt file of known aircraft you want to
#       assign a specific CoT type based on
#  FlightID AND/OR ICAO HEX address.
def dolphin(flight: Optional[Union[bytes, str]] = None, affil: Optional[Union[bytes, str]] = None) -> bool:
    """
    Classify an aircraft as USCG Dolphin helicopter.

    MH-65D Dolphins out of Air Station SF use older ADS-B, but luckily have a similar
    "flight" name pattern (C6xxxx).
    
    Args:
        flight: Flight ID/callsign to check
        affil: Affiliation code (should be 'M' for military)

    Returns:
        True if aircraft is identified as USCG Dolphin, False otherwise
        
    Examples:
        * C6540 / AE2682 https://globe.adsbexchange.com/?icao=ae2682
        * C6604 / AE26BB https://globe.adsbexchange.com/?icao=ae26bb
    """
    mereswine = False
    if flight and len(flight) >= 3 and flight[:2] in ["C6", b"C6"]:
        if affil and affil in ["M", b"M"]:
            mereswine = True
    return mereswine


# flight ID is limited to 8 digits in the DO-260B specification
def adsb_to_cot_type(
    icao: Union[bytes, int, str],
    category: Optional[Union[bytes, int, str]] = None,
    flight: Optional[Union[bytes, str]] = None,
) -> str:
    """
    Classify Cursor on Target Event Type from ICAO address.
    
    Args:
        icao: ICAO address (hex string, bytes, or int)
        category: ADS-B DO-260B or GDL90 Emitter Category (optional)
        flight: Flight ID/callsign (optional)
    
    Returns:
        CoT Event Type string (e.g., 'a-n-A-C-F')
    """
    affil = "C"  # Affiliation, default = Civilian
    attitude = "u"  # Attitude, default = unknown

    # TODO: If the adsbx has a leading underscore and registry "_N1234A" then that means they are calculating the
    #  registration with no Flight ID field transmited
    # TODO: If no specific country allocated ICAO address range, e.g. "country": "Rsrvd (ICAO SAM Region)" or
    #  "country": "ICAO (special use)" set
    #         OMMIT {affil}
    #         {attitude} = u    (unknown)

    # The "~" is a adsbexchange (possibly a few others) visual customization to indicate a non (MLAT, ADS-B ICAO hex)
    # ADS-B track injected by the FAA via the ADS-B rebroadcast, usually FAA Secondary Radar Mode A/C tracks for safety
    # and ground vehicles
    if isinstance(icao, str):
        icao = int(f"0x{icao.replace('~', '')}", 16)
    elif isinstance(icao, int):
        icao = icao

    attitude = set_domestic_us(flight, attitude)

    attitude = is_tw(icao, attitude)

    attitude, affil = set_neutral_civ(icao, attitude, affil)

    attitude = is_known_country_icao(icao, attitude)

    attitude, affil = set_friendly_mil(icao, attitude, affil)

    cot_type = f"a-{attitude}-A-{affil}"

    if category:
        cot_type, affil = cot_type_from_category(category, attitude, affil, cot_type)

    cot_type = is_dolphin(affil, cot_type, flight)

    return cot_type


def cot_type_from_category(
    category: Union[int, bytes],
    attitude: bytes,
    affil: bytes,
    cot_type: Optional[bytes] = None,
) -> tuple:
    """Determine the CoT Event Type from the given ADS-B Category."""
    _category = str(category)

    # Fixed wing. No CoT exists to further categorize based on DO-260B/GDL90 emitter catagory, cannot determine if
    # Cargo, Passenger, or other without additional info.
    if _category in ["1", "2", "3", "4", "5", "A1", "A2", "A3", "A4", "A5"]:
        cot_type = f"a-{attitude}-A-{affil}-F"
    # Fixed wing. High Performance (basically a fighter jet) type="a-.-A-M-F-F" capable: >5g & >400 knots
    elif _category in ["6", "A6"]:
        # Force the MIL {affil} "F" icon for fast mover, even if a civil ICAO address, no pink/magenta 2525 icon
        # exists; just = s_apmff--------.png
        affil = "M"
        cot_type = f"a-{attitude}-A-{affil}-F-F"
    # Rotor/Helicopter
    elif _category in ["7", "A7"]:
        cot_type = f"a-{attitude}-A-{affil}-H"
    # Glider/sailplane
    elif _category in ["9", "B1"]:
        cot_type = f"a-{attitude}-A-{affil}-F"
    # Lighter-than-air, Balloon
    elif _category in ["10", "B2"]:
        cot_type = f"a-{attitude}-A-{affil}-L"
    # Drone/UAS/RPV
    elif _category in ["14", "B6"]:
        # This will have to have {affil}=M to generate a 2525B marker in TAK.
        # Cannot be CIV "C" as no CIV drone icons exist for 2525B
        affil = "M"
        cot_type = f"a-{attitude}-A-{affil}-F-Q"
    # Space/Trans-atmospheric vehicle. (e.g SpaceX, Blue Origin, Virgin Galactic)
    elif _category in ["15", "B7"]:
        # Will having -P- affect anything??? ...different than line 223.
        cot_type = f"a-{attitude}-P-{affil}"
    # Surface Vehicle. Includes emergency and service vehicles, as there is no specific 2525B icon for each.
    elif _category in ["17", "18", "C1", "C2"]:
        cot_type = f"a-.-G-E-V-C-U"
    # elif _category in ["17", "C1"]:  #  ***OPTION***  Surface Vehicle - Emergency Vehicle
    #     cot_type = f"a-.-G-E-V-U-A"   # MILSTD 2525B icon = Ambulance (blue circle w/ Cross)
    # "point obstacle (includes tethered ballons)" & "cluster obstacles" i.e. fixed tower -
    #   radio, beacon, tethered ballons, etc  (MILSTD 2525 "D" has a tethered balloon icon that "B" doesn't)
    elif _category in ["19", "20", "C3", "C4"]:
        cot_type = f"a-{attitude}-G-I-U-T-com-tow"
    # This catagory is for all the "No ADS-B Emitter Catagory Information" undefined/unattributed/reserved
    # emmitter catagories in DO-260B/GDL90.
    # adsbexchange will often set A0 for MLAT (TCAS or MODE-S only transponders) tracks
    # add elif or if for:
    #   if no definitive {attitude} and {affil} possible, for the UNKNOWN DO-260B/GDL90 emmitter catagories,
    #   make cot_type = a-u-A
    elif _category in [
        "0",
        "8",
        "13",
        "16",
        "22",
        "23",
        "24",
        "25",
        "26",
        "27",
        "28",
        "29",
        "30",
        "31",
        "32",
        "33",
        "34",
        "35",
        "36",
        "37",
        "38",
        "39",
        "A0",
        "B0",
        "B5",
        "C0",
        "C6",
        "C7",
        "D0",
        "D1",
        "D2",
        "D3",
        "D4",
        "D5",
        "D6",
        "D7",
    ]:
        cot_type = f"a-{attitude}-A-{affil}"

    return cot_type, affil


def is_dolphin(affil: str, cot_type: str, flight: Optional[Union[bytes, str]]) -> str:
    """
    Check if aircraft is USCG Dolphin and update CoT type accordingly.
    
    Args:
        affil: Affiliation code
        cot_type: Current CoT type
        flight: Flight ID/callsign
    
    Returns:
        Updated CoT type string
    """
    if dolphin(flight, affil):
        # -H-H is CSAR rotary wing 2525B icon
        cot_type = f"a-f-A-{affil}-H-H"
    return cot_type


def get_icao_range(range_type: str = "CIV") -> list:
    return _RANGE_CACHE.get(range_type, [])


def icao_in_known_range(icao_int, range_type: str = "CIV") -> bool:
    """Determine if the given ICAO is within a known 'friendly' ICAO Range."""
    friendly = False
    for idx in get_icao_range(range_type):
        if (
            DEFAULT_HEX_RANGES[idx]["start"]
            <= icao_int
            <= DEFAULT_HEX_RANGES[idx]["end"]
        ):
            friendly = True
    return friendly


def set_friendly_mil(icao: int, attitude: str = "u", affil: str = "") -> tuple:
    """Set Affiliation and Attitude for 'friendly' Military ICAOs."""
    if icao_in_known_range(icao, "MIL"):
        affil = "M"
        attitude = "f"
    return attitude, affil


def set_neutral_civ(icao: int, attitude: str = "u", affil: str = "") -> tuple:
    """Set Affiliation and Attitude for known 'neutral' Civilian ICAOs."""
    if icao_in_known_range(icao):
        affil = "C"
        attitude = "n"
    return attitude, affil


def is_known_country_icao(icao: int, attitude: str = "u"):
    """Determine if the given ICAO is from a known country."""
    if lookup_country(icao):
        attitude = "n"
    return attitude


def get_civ() -> list:
    """Get a List of Known 'friendly' Civilian ICAO Ranges."""
    return list(filter(lambda x: "-CIV" in x, DEFAULT_HEX_RANGES))


def is_civ(icao: int) -> str:
    """Determine if the given ICAO is within the 'Civilian' ICAO ranges."""
    civ_icao = False
    for civ in get_civ():
        if (
            DEFAULT_HEX_RANGES[civ]["start"]
            <= icao
            <= DEFAULT_HEX_RANGES[civ]["end"]
        ):
            civ_icao = True
    return civ_icao


def is_tw(icao: int, attitude: str = "u") -> str:
    """Determine if the given ICAO is from the Taiwan range."""
    tw_start = 0x899000
    tw_end = 0x8993FF
    if tw_start <= icao <= tw_end:
        attitude = "n"
    return attitude


# TODO: Eliminate this if section, as it will already be coded as neutral civil cot
#       type if left alone which fits the cot framework.
def set_domestic_us(flight: Optional[bytes] = None, attitude: str = "u") -> str:
    """Set the COT Attitude to neutral if the flight is from a known domestic US airline."""
    if flight:
        for dom in DOMESTIC_US_AIRLINES:
            if flight.startswith(dom):
                attitude = "n"
    return attitude


def get_hae(alt_geom: float = 0.0) -> str:
    """
    Calculate height above ellipsoid (HAE) in meters from geometric altitude in feet.

    Args:
        alt_geom: Geometric (GNSS/INS) altitude in feet referenced to WGS84 ellipsoid
    
    Returns:
        HAE in meters as string, or DEFAULT_COT_VAL if alt_geom is 0/falsy
    """
    if alt_geom:
        hae = alt_geom * 0.3048
    else:
        hae = DEFAULT_COT_VAL
    return str(hae)


def get_speed(gs: float = 0.0) -> str:
    """
    Convert ground speed from knots to meters per second.
    
    Args:
        gs: Ground speed in knots
    
    Returns:
        Speed in m/s as string, or DEFAULT_COT_VAL if gs is 0/falsy
    """
    if gs:
        speed = gs * 0.514444
    else:
        speed = DEFAULT_COT_VAL
    return str(speed)


def set_name_callsign(
    icao: str,
    reg: Optional[str] = None,
    craft_type: Optional[str] = None,
    flight: Optional[str] = None,
    known_craft: Optional[dict] = None,
) -> Tuple[str, str]:
    """
    Set the Name and Callsign in the CoT Event.
    
    Args:
        icao: ICAO hex address
        reg: Aircraft registration (optional)
        craft_type: Aircraft type (optional)
        flight: Flight ID/callsign (optional)
        known_craft: Known aircraft data dict (optional)
    
    Returns:
        Tuple of (name, callsign) strings
    """
    if known_craft is None:
        known_craft = {}
    name: str = known_craft.get("CALLSIGN")
    if name:
        callsign = name
    else:
        name = f"ICAO-{icao}"
        if flight and reg and craft_type:
            callsign = "-".join([flight.strip().upper(), reg, craft_type])
        elif reg and craft_type:
            callsign = "-".join([reg, craft_type])
        elif flight:
            callsign = flight.strip().upper()
        elif reg:
            callsign = reg
        else:
            callsign = name
    callsign = f"{callsign} ({icao})"
    return name, callsign


def set_category(category: Optional[Union[str, int]], known_craft: Optional[dict] = None) -> Union[str, int, None]:
    """
    Set the category for the given aircraft if a transform exists in known_craft.
    
    Args:
        category: Current category code
        known_craft: Known aircraft data dict (optional)
    
    Returns:
        Updated category code or original if no transform found
    """
    if known_craft is None:
        known_craft = {}
    cot_type = known_craft.get("COT")
    if not cot_type:
        known_type = known_craft.get("TYPE", "").strip().upper()
        if known_type:
            if known_type == "FIXED WING":
                category = "1"
            elif known_type == "HELICOPTER":
                category = "7"
            elif known_type == "UAS":
                category = "14"
            else:
                category = known_type
    return category


def set_cot_type(icao_hex: str, category: Optional[Union[str, int]], flight: Optional[Union[str, bytes]], known_craft: dict) -> str:
    """
    Set the CoT Type for the given aircraft if a transform exists in known_craft.
    
    Args:
        icao_hex: ICAO hex address
        category: Aircraft category code
        flight: Flight ID/callsign
        known_craft: Known aircraft data dict
    
    Returns:
        CoT type string
    """
    cot_type = known_craft.get("COT")
    if not cot_type:
        cot_type = adsb_to_cot_type(icao_hex, category, flight)
    return cot_type


def icao_int_to_hex(addr) -> str:
    """Convert ICAO from integer to hexidecimal."""
    return str(hex(addr)).lstrip("0x").upper()


def read_known_craft(known_file: str) -> dict:
    """
    Load known aircraft database from CSV or JSON with optimized O(1) lookup by hex or registration.
    
    Supports two formats:
    - CSV: columns HEX, REG, COT, etc.
    - JSON: array of objects with hexid/reg/cot or HEX/REG/COT fields
    
    Args:
        known_file: Path to CSV or JSON file with known aircraft data
    
    Returns:
        Dict with 'rows' (all data), 'hex_index' (ICAO hex -> row), and 'reg_index' (registration -> row)
    """
    all_rows = []
    
    # Try to determine format by file extension
    is_json = known_file.lower().endswith('.json')
    
    with open(known_file, encoding="UTF-8") as kfd:
        if is_json:
            import json
            data = json.load(kfd)
            # Handle both direct array and nested {"aircraft": [...]} format
            if isinstance(data, dict) and "aircraft" in data:
                all_rows = data["aircraft"]
            elif isinstance(data, list):
                all_rows = data
            else:
                all_rows = []
            
            # Normalize field names to uppercase for consistency
            normalized_rows = []
            for row in all_rows:
                normalized = {}
                for key, value in row.items():
                    # Map common variations to standard field names
                    upper_key = key.upper()
                    if key.lower() in ('hexid', 'hex', 'icao'):
                        normalized['HEX'] = value
                    elif key.lower() in ('reg', 'registration', 'tail'):
                        normalized['REG'] = value
                    elif key.lower() in ('cot', 'type_cot', 'cottype', 'cot type'):
                        normalized['COT'] = value
                    else:
                        normalized[upper_key] = value
                normalized_rows.append(normalized)
            all_rows = normalized_rows
        else:
            # CSV format
            # Skip comment lines and find header or use default fieldnames
            lines = []
            header = None
            for line in kfd:
                stripped = line.strip()
                if not stripped or stripped.startswith('#'):
                    # Check if this is a format line that tells us the fields
                    if 'hexid' in stripped.lower() and 'registration' in stripped.lower():
                        # Extract field names from comment
                        parts = stripped.strip('#').strip().split(',')
                        header = [p.strip().strip('"') for p in parts]
                    continue
                lines.append(line)
            
            # Reset to read the non-comment lines
            if header:
                reader = csv.DictReader(lines, fieldnames=header)
            else:
                # Try to auto-detect from first line
                reader = csv.DictReader(lines)
            
            raw_rows = list(reader)
            
            # Normalize CSV field names too (handle quoted headers, variations, etc.)
            normalized_rows = []
            for row in raw_rows:
                normalized = {}
                for key, value in row.items():
                    # Skip None keys (extra columns)
                    if key is None:
                        continue
                    
                    # Remove quotes from keys and values if present
                    clean_key = key.strip().strip('"').strip()
                    clean_value = value.strip().strip('"').strip() if value else ""
                    
                    # Skip empty keys
                    if not clean_key or clean_key.startswith('#'):
                        continue
                    
                    # Map common variations to standard field names
                    key_lower = clean_key.lower()
                    if key_lower in ('hexid', 'hex', 'icao'):
                        normalized['HEX'] = clean_value
                    elif key_lower in ('reg', 'registration', 'tail'):
                        normalized['REG'] = clean_value
                    elif key_lower in ('cot', 'type_cot', 'cottype', 'cot type'):
                        normalized['COT'] = clean_value
                    else:
                        # Keep other fields with uppercase key
                        normalized[clean_key.upper()] = clean_value
                
                # Only add rows that have at least HEX or REG
                if normalized.get('HEX') or normalized.get('REG'):
                    normalized_rows.append(normalized)
            
            all_rows = normalized_rows
    
    # Build hash indexes for O(1) lookups by both HEX and REG
    hex_index = {}
    reg_index = {}
    for row in all_rows:
        hex_val = row.get("HEX", "").strip().upper()
        if hex_val:
            hex_index[hex_val] = row
        
        reg_val = row.get("REG", "").strip().upper()
        if reg_val:
            reg_index[reg_val] = row
    
    return {"rows": all_rows, "hex_index": hex_index, "reg_index": reg_index}


def get_known_craft(filter_db: dict, icao_hex: Optional[str] = None, reg: Optional[str] = None) -> dict:
    """
    Perform O(1) lookup of known aircraft by ICAO hex address or registration (tail number).
    
    Args:
        filter_db: Database dict from read_known_craft()
        icao_hex: ICAO hex address to lookup (optional)
        reg: Aircraft registration/tail number to lookup (optional)
    
    Returns:
        Aircraft data dict or empty dict if not found
    
    Note:
        If both icao_hex and reg are provided, hex lookup takes precedence.
        If neither is provided, returns empty dict.
    """
    if not filter_db:
        return {}
    
    # Try hex lookup first if provided
    if icao_hex:
        result = filter_db.get("hex_index", {}).get(icao_hex.strip().upper())
        if result:
            return result
    
    # Try registration lookup if provided
    if reg:
        result = filter_db.get("reg_index", {}).get(reg.strip().upper())
        if result:
            return result
    
    return {}