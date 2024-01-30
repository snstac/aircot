#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright Sensors & Signals LLC https://www.snstac.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""AirCoT Module Tests."""

import asyncio
import pprint
import urllib

import pytest

import aircot

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"


def test_hex_country_lookup():
    """
    Looks up an ICAO for Barzil and ensures the function returns the right country (Brazil!)
    """
    brazil = 0xE40000
    country = aircot.functions.lookup_country(brazil)
    assert country == "Brazil"


def test_dolphin():
    flight = "C61234"
    affil = "M"
    is_dolphin = aircot.functions.dolphin(flight, affil)
    assert is_dolphin == True


def test_set_domestic_us():
    flight = "UAL2153"
    attitude = "."
    new_attitude = aircot.functions.set_domestic_us(flight, attitude)
    assert new_attitude == "n"


def test_negative_set_domestic_us():
    flight = "SA123"
    attitude = "."
    new_attitude = aircot.functions.set_domestic_us(flight, attitude)
    assert new_attitude == "."


def test_adsb_to_cot_type():
    icao = "a61d00"
    category = "A3"
    flight = "UAL2153"
    x = aircot.adsb_to_cot_type(icao, category, flight)
    assert x == "a-n-A-C-F"


def test_get_icao_range():
    ranges = aircot.functions.get_icao_range()
    assert ["US-CIV", "CAN-CIV", "NZ-CIV", "AUS-CIV", "UK-CIV"] == ranges


def test_get_icao_range_mil():
    ranges = aircot.functions.get_icao_range("MIL")
    assert ["US-MIL", "CAN-MIL", "NZ-MIL", "AUS-MIL", "UK-MIL"] == ranges


def test_negative_get_icao_range():
    ranges = aircot.functions.get_icao_range("FOO")
    assert [] == ranges


def test_icao_in_range():
    icao = 0xC80000  # NZ-CIV Range
    in_range = aircot.functions.icao_in_known_range(icao)
    assert in_range == True


def test_set_neutral_civ():
    icao = 0xC80000  # NZ-CIV Range
    attitude, affil = aircot.functions.set_neutral_civ(icao)
    assert affil == "C"
    assert attitude == "n"


def test_negative_set_neutral_civ():
    icao = 0xC87F00  # NZ-MIL Range
    attitude, affil = aircot.functions.set_neutral_civ(icao)
    assert "" == affil
    assert "u" == attitude


def test_icao_in_range_mil():
    icao = 0xC87F00  # NZ-MIL Range
    in_range = aircot.functions.icao_in_known_range(icao, "MIL")
    assert in_range == True


def test_set_friendly_mil():
    icao = 0xC87F00  # NZ-MIL Range
    attitude, affil = aircot.functions.set_friendly_mil(icao)
    assert affil == "M"
    assert attitude == "f"


def test_negative_set_friendly_mil():
    icao = 0xC80000  # NZ-CIV Range
    attitude, affil = aircot.functions.set_friendly_mil(icao)
    assert "" == affil
    assert "u" == attitude


def test_cot_type_from_category_A5():
    category = "A5"
    attitude = "u"
    affiliation = "C"
    cot_type, affil = aircot.functions.cot_type_from_category(
        category, attitude, affiliation
    )
    assert cot_type == "a-u-A-C-F"
    assert affil == "C"


def test_cot_type_from_category_A6():
    category = "A6"
    attitude = "f"
    affiliation = "x"
    cot_type, affil = aircot.functions.cot_type_from_category(
        category, attitude, affiliation
    )
    assert cot_type == "a-f-A-M-F-F"
    assert affil == "M"


def test_cot_type_from_category_B6():
    category = "B6"
    attitude = "f"
    affiliation = "x"
    cot_type, affil = aircot.functions.cot_type_from_category(
        category, attitude, affiliation
    )
    assert cot_type == "a-f-A-M-F-Q"
    assert affil == "M"


def test_cot_type_from_category_D6():
    category = "D6"
    attitude = "f"
    affiliation = "C"
    cot_type, affil = aircot.functions.cot_type_from_category(
        category, attitude, affiliation
    )
    assert cot_type == "a-f-A-C"
    assert affil == "C"


def test_get_hae():
    alt_geom = 38650
    hae = aircot.functions.get_hae(alt_geom)
    assert hae == "11780.52"


def test_negative_get_hae():
    alt_geom = ""
    hae = aircot.functions.get_hae(alt_geom)
    assert hae == "9999999.0"


def test_get_speed():
    gs = 79.5
    speed = aircot.functions.get_speed(gs)
    assert speed == "40.898298000000004"


def test_negative_get_speed():
    gs = ""
    speed = aircot.functions.get_speed(gs)
    assert speed == "9999999.0"


def test_negative_set_neutral_civ_lux():
    icao = 0x4D0223  # from sn
    affil, attitude = aircot.functions.set_neutral_civ(icao)
    assert "u" == affil
    assert "" == attitude


def test_adsb_to_cot_type_lux():
    icao = 0x4D0223
    category = "1"
    flight = "SVW20E"
    cot_type = aircot.adsb_to_cot_type(icao, category, flight)
    assert "a-n-A-C-F" == cot_type


def test_set_name_callsign_icao():
    # icao: str, reg, craft_type, flight, known_craft = {}
    icao = "icao123"
    reg = "reg123"
    craft_type = "craft_type123"
    flight = "flight123"
    name, callsign = aircot.set_name_callsign(icao)
    assert "ICAO-icao123" == name
    assert "ICAO-icao123" == callsign


def test_set_name_callsign_icao_reg():
    # icao: str, reg, craft_type, flight, known_craft = {}
    icao = "icao123"
    reg = "reg123"
    craft_type = "craft_type123"
    flight = "flight123"
    name, callsign = aircot.set_name_callsign(icao, reg)
    assert "ICAO-icao123" == name
    assert "reg123" == callsign


def test_set_name_callsign_icao_reg_craft_type():
    # icao: str, reg, craft_type, flight, known_craft = {}
    icao = "icao123"
    reg = "reg123"
    craft_type = "craft_type123"
    flight = "flight123"
    name, callsign = aircot.set_name_callsign(icao, reg, craft_type)
    assert "ICAO-icao123" == name
    assert "reg123-craft_type123" == callsign


def test_set_name_callsign_icao_reg_craft_type_flight():
    # icao: str, reg, craft_type, flight, known_craft = {}
    icao = "icao123"
    reg = "reg123"
    craft_type = "craft_type123"
    flight = "flight123"
    name, callsign = aircot.set_name_callsign(icao, reg, craft_type, flight)
    assert "ICAO-icao123" == name
    assert "FLIGHT123-reg123-craft_type123" == callsign


def test_set_name_callsign_icao_flight():
    # icao: str, reg, craft_type, flight, known_craft = {}
    icao = "icao123"
    reg = "reg123"
    craft_type = "craft_type123"
    flight = "flight123"
    name, callsign = aircot.set_name_callsign(icao, flight=flight)
    assert "ICAO-icao123" == name
    assert "FLIGHT123" == callsign


def test_knowndb_csv():
    """Test reading KnownDB CSV file with aircraft classifying hints."""
    known_db = aircot.read_known_craft("tests/data/example-known_craft.csv")
    known_craft: dict = aircot.get_known_craft(known_db, "N17085", "REG")
    assert known_craft["COT"] == "a-f-A-C-F"


def test_adsbid_json():
    """Test reading ADSB ID DB JSON file with aircraft classifying hints."""
    known_db = aircot.read_known_craft("tests/data/cotdb.json")
    known_craft: dict = aircot.get_known_craft(known_db, "e49555", filter_key="HEXID")
    assert known_craft["COT"] == "a-f-A-M-F-U-M"
