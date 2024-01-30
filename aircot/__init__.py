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

"""Aircraft classifier for TAK.

:source: <https://github.com/snstac/aircot>
"""

__version__ = "2.0.0-beta3"
__author__ = "Greg Albrecht <gba@snstac.com>"
__copyright__ = "Copyright Sensors & Signals LLC https://www.snstac.com"
__license__ = "Apache License, Version 2.0"

# Python 3.6 test/build work-around:
try:
    from .constants import (  # NOQA
        LOG_FORMAT,
        LOG_LEVEL,
        DEFAULT_COT_STALE,
        DEFAULT_HEX_RANGES,
        DOMESTIC_US_AIRLINES,
        ICAO_RANGES,
        ISO_8601_UTC,
        DEFAULT_COT_VAL,
    )

    from .functions import (  # NOQA
        adsb_to_cot_type,
        dolphin,
        lookup_country,
        cot_type_from_category,
        is_dolphin,
        get_icao_range,
        icao_in_known_range,
        set_friendly_mil,
        set_neutral_civ,
        is_known_country_icao,
        get_civ,
        is_civ,
        is_tw,
        set_domestic_us,
        get_hae,
        get_speed,
        set_name_callsign,
        set_category,
        set_cot_type,
        icao_int_to_hex,
        read_known_craft,
        get_known_craft,
    )

except ImportError as exc:
    import warnings

    warnings.warn(str(exc))
    warnings.warn("ADSBCOT ignoring ImportError - Python 3.6 compat work-around.")
