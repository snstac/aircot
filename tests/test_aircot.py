#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""AirCoT Module Tests."""

import asyncio
import urllib

import pytest

import aircot
import aircot.functions

__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Orion Labs, Inc."
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
    in_range = aircot.functions.icao_in_range(icao)
    assert in_range == True


def test_icao_in_range_mil():
    icao = 0xC87F00  # NZ-MIL Range
    in_range = aircot.functions.icao_in_range(icao, "MIL")
    assert in_range == True


def test_set_friendly_mil():
    icao = 0xC87F00  # NZ-MIL Range
    affil, attitude = aircot.functions.set_friendly_mil(icao)
    assert affil == "M"
    assert attitude == "f"


def test_negative_set_friendly_mil():
    icao = 0xC80000  # NZ-CIV Range
    affil, attitude = aircot.functions.set_friendly_mil(icao)
    assert affil == ""
    assert attitude == "."


def test_cot_type_from_category_A5():
    category = "A5"
    attitude = "u"
    affiliation = "C"
    cot_type, affil = aircot.functions.cot_type_from_category(category, attitude, affiliation)
    assert cot_type == "a-u-A-C-F"
    assert affil == "C"


def test_cot_type_from_category_A6():
    category = "A6"
    attitude = "f"
    affiliation = "x"
    cot_type, affil = aircot.functions.cot_type_from_category(category, attitude, affiliation)
    assert cot_type == "a-f-A-M-F-F"
    assert affil == "M"


def test_cot_type_from_category_B6():
    category = "B6"
    attitude = "f"
    affiliation = "x"
    cot_type, affil = aircot.functions.cot_type_from_category(category, attitude, affiliation)
    assert cot_type == "a-f-A-M-F-Q"
    assert affil == "M"


def test_cot_type_from_category_D6():
    category = "D6"
    attitude = "f"
    affiliation = "C"
    cot_type, affil = aircot.functions.cot_type_from_category(category, attitude, affiliation)
    assert cot_type == "a-f-A-C"
    assert affil == "C"
