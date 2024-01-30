#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

import csv
import json

from typing import Optional, Union

import aircot

__author__ = "Greg Albrecht <gba@snstac.com>"
__copyright__ = "Copyright Sensors & Signals LLC https://www.snstac.com"
__license__ = "Apache License, Version 2.0"


def lookup_country(icao: bytes) -> Optional[bytes]:
    """
    Lookup ICAO within each country range and return the associated country.
    """
    country = None
    for country_dict in aircot.ICAO_RANGES:
        if country_dict["start"] <= icao <= country_dict["end"]:
            country = country_dict["country"]
    return country


# TODO: Pull this out into a custom csv or txt file of known aircraft you want to
#       assign a specific CoT type based on
#  FlightID AND/OR ICAO HEX address.
def dolphin(flight: Optional[bytes] = None, affil: Optional[bytes] = None) -> bool:
    """
    Classify an aircraft as USCG Dolphin.

    MH-65D Dolphins out of Air Station SF use older ADS-B, but luckily have a similar
    "flight" name.

    For example:
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
    icao: Union[bytes, int],
    category: Optional[bytes] = None,
    flight: Optional[bytes] = None,
) -> bytes:
    """
    Classify Cursor on Target Event Type from ICAO address (binary, decimal, octal, or hex; and if available, from
    ADS-B DO-260B or GDL90 Emitter Category & Flight ID.
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


def is_dolphin(affil, cot_type, flight):
    """Call dolphin() with cot type and flight."""
    if dolphin(flight, affil):
        # -H-H is CSAR rotary wing 2525B icon
        cot_type = f"a-f-A-{affil}-H-H"
    return cot_type


def get_icao_range(range_type: str = "CIV") -> list:
    """Gets a List of known 'friendly' ICAO Ranges of a given type (CIV|MIL)."""
    return list(filter(lambda x: f"-{range_type}" in x, aircot.DEFAULT_HEX_RANGES))


def icao_in_known_range(icao_int, range_type: str = "CIV") -> bool:
    """Determine if the given ICAO is within a known 'friendly' ICAO Range."""
    friendly = False
    for idx in get_icao_range(range_type):
        if (
            aircot.DEFAULT_HEX_RANGES[idx]["start"]
            <= icao_int
            <= aircot.DEFAULT_HEX_RANGES[idx]["end"]
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
    return list(filter(lambda x: "-CIV" in x, aircot.DEFAULT_HEX_RANGES))


def is_civ(icao: int) -> str:
    """Determine if the given ICAO is within the 'Civilian' ICAO ranges."""
    civ_icao = False
    for civ in get_civ():
        if (
            aircot.DEFAULT_HEX_RANGES[civ]["start"]
            <= icao
            <= aircot.DEFAULT_HEX_RANGES[civ]["end"]
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
        for dom in aircot.DOMESTIC_US_AIRLINES:
            if flight.startswith(dom):
                attitude = "n"
    return attitude


def get_hae(alt_geom: float = 0.0) -> str:
    """
    Calculate the height above ellipsoid HAE in meters for the given geometric altitude in feet.

    :param alt_geom: geometric (GNSS / INS) altitude in feet referenced to the WGS84 ellipsoid.
    """
    if alt_geom:
        hae = alt_geom * 0.3048
    else:
        hae = aircot.DEFAULT_COT_VAL
    return str(hae)


def get_speed(gs: float = 0.0):
    # gs: ground speed in knots
    if gs:
        speed = gs * 0.514444
    else:
        speed = aircot.DEFAULT_COT_VAL
    return str(speed)


def set_name_callsign(
    icao: str,
    reg=None,
    craft_type=None,
    flight=None,
    known_craft: Optional[list] = None,
):
    """
    Set the Name and Callsign in the COT Event.
    Populates the fields with ICAO, Reg, Craft Type and Flight data, if available.
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
    return name, callsign


def set_category(category, known_craft: Optional[list] = None):
    """Set the category for the given aircraft if a transform exists in known_craft."""
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


def set_cot_type(icao_hex, category, flight, known_craft):
    """Set the COT Type for the given aircraft if a transform exists in known_craft."""
    cot_type = known_craft.get("COT")
    if not cot_type:
        cot_type = aircot.adsb_to_cot_type(icao_hex, category, flight)
    return cot_type


def icao_int_to_hex(addr) -> str:
    """Convert ICAO from integer to hexidecimal."""
    return str(hex(addr)).lstrip("0x").upper()


def capitalize(small_dict):
    """Capitlize the keys in the given dict."""
    big_dict = small_dict
    if isinstance(small_dict, list):
        big_dict = [capitalize(v) for v in small_dict]
    elif isinstance(small_dict, dict):
        big_dict = {k.upper(): capitalize(v) for k, v in small_dict.items()}
    return big_dict


def read_known_craft(known_file: bytes) -> list:
    """Reads the FILTER_CSV file into a `list`"""
    # DOMAIN,AGENCY,REG,CALLSIGN,TYPE,MODEL,HEX,COT,TYPE,,
    all_rows = []
    with open(known_file, encoding="UTF-8") as kfd:
        reader = csv.DictReader(kfd)
        for row in reader:
            all_rows.append(row)
        if not all_rows:
            kfd.seek(0)
            j_db = json.load(kfd)
            all_rows = capitalize(j_db.get("aircraft", []))
    return all_rows


def get_known_craft(
    filter_db: dict, filter_value: str, filter_key: str = "HEX"
) -> dict:
    """Get the known craft 'data transform' from the known craft db."""
    known_craft = {}
    if filter_db:
        known_craft = (
            list(
                filter(
                    lambda x: x[filter_key].strip().upper()
                    == filter_value.strip().upper(),
                    filter_db,
                )
            )
            or [{}]
        )[0]

    return known_craft
