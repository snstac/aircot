#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2022 Greg Albrecht <oss@undef.net>
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
# Author:: Greg Albrecht W2GMD <oss@undef.net>
#

"""
Cursor-On-Target Aircraft classification Module.
~~~~

:author: Greg Albrecht W2GMD <oss@undef.net>
:copyright: Copyright 2022 Greg Albrecht
:license: Apache License, Version 2.0
:source: <https://github.com/ampledata/aircot>

"""

from .constants import (
    LOG_LEVEL,
    LOG_FORMAT,  # NOQA
    DOMESTIC_US_AIRLINES,
    DEFAULT_HEX_RANGES,
    DEFAULT_COT_STALE,
    ICAO_RANGES,
    ISO_8601_UTC,
)

from .functions import (
    adsb_to_cot_type,
    set_name_callsign,
    icao_int_to_hex,
    read_known_craft,
    set_category,
    set_cot_type,
    get_known_craft,
)  # NOQA


__author__ = "Greg Albrecht W2GMD <oss@undef.net>"
__copyright__ = "Copyright 2022 Greg Albrecht"
__license__ = "Apache License, Version 2.0"
