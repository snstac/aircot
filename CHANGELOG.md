## AirCOT 4.0.0

- Happy 2026!
- Rewritten and optimized.
- Added embedded TAK-ADSB-ID from @sgofferj (Fixes #9)

## AirCOT 3.0.0

Happy Summer Solstice

- Rewrote GitHub actions, moved most logic to shell script and Makefile.
- Renamed Debian package from python3-aircot to aircot.
- Standardized Makefile for all PyTAK based programs.
- Cleaned, simplified and expanded documentation.
- Created Makefile jobs for Debian packaging and PyTAK customization.
- Moved all media to media sub directory under docs/.
- Converted README.rst to README.md.
- Style & Linting of code.


## AirCOT 2.0.0

- New for 2024!
- Added RTFD documentation site.
- Code style, linting cleanup.
- Fixes #1: ValueError: invalid literal for int() with base 16.
- Fixes #3: Add testing support for Python 3.10 - 3.12.
- Fixes #4: Add RTFD documentation site.
- Fixes #5: Ensure Python 3.6 testing works.
- Fixes #6: Time format is W3C_XML_DATETIME, not ISO_8601_UTC.
- Fixes #7: Move package metadata to setup.cfg from setup.py.
- Fixes #8: Add support for TAK-ADSB-ID.
