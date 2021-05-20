#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python Team Awareness Kit (PyTAK) Module.

"""
Python Team Awareness Kit (PyTAK) Module.
~~~~


:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2021 Orion Labs, Inc.
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aircot>

"""

from .constants import (LOG_LEVEL, LOG_FORMAT,  # NOQA
                        DOMESTIC_US_AIRLINES, DEFAULT_HEX_RANGES,
                        DEFAULT_COT_STALE, ICAO_RANGES, ISO_8601_UTC)

from .functions import adsb_to_cot_type, set_name_callsign, icao_int_to_hex, read_known_craft, set_category, set_cot_type  # NOQA


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2021 Orion Labs, Inc."
__license__ = "Apache License, Version 2.0"
