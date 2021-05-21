aircot - Cursor on Target (CoT) Classifiers for ADS-B & Aircraft data.
**********************************************************************
**IF YOU HAVE AN URGENT OPERATIONAL NEED**: Email ops@undef.net or call/sms +1-415-598-8226

AirCoT is a Python Module with functions & methods for Cursor on Target (CoT) Event typing/classifying of aircraft
based on ADS-B data.

Examples of software clients using the AirCoT:

* `adsbcot <https://github.com/ampledata/adsbcot>`_: Automatic Dependent Surveillance-Broadcast (ADS-B) to Cursor on Target (CoT) Gateway. Transforms ADS-B position messages to CoT PLI Events.
* `adsbxcot <https://github.com/ampledata/adsbxcot>`_: ADS-B Exchange to Cursor on Target (CoT) Gateway. Transforms ADS-B position messages to CoT PLI Events.
* `stratuxcot <https://github.com/ampledata/stratuxcot>`_: Stratux ADS-B to Cursor on Target (CoT) Gateway. Transforms position messages to CoT PLI Events.

Support AirCot Development
==========================

AirCoT has been developed for the Disaster Response, Public Safety and Frontline community at-large. This software is
currently provided at no-cost to our end-users. All development is self-funded and all time-spent is entirely
voluntary. Any contribution you can make to further these software development efforts, and the mission of AirCoT to
provide ongoing SA capabilities to our end-users, is greatly appreciated:

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support AirCot development: Buy me a coffee!


Requirements
============

AirCoT requires Python 3.6 or above and WILL NOT work on Python versions below 3.6 (that means no Python 2 support).

Installation
============

AirCoT is installed as a dependency for various other programs (see above) but can be installed and updated
independently.

Installing as a Debian/Ubuntu Package::

    $ wget https://github.com/ampledata/aircot/releases/latest/download/python3-aircot_latest_all.deb
    $ sudo apt install -f ./python3-aircot_latest_all.deb

Install from the Python Package Index::

    $ pip install aircot


Install from this source tree::

    $ git clone https://github.com/ampledata/aircot.git
    $ cd aircot/
    $ python setup.py install


Source
======
Github: https://github.com/ampledata/aircot

Author
======
Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/

Copyright
=========
AirCoT is Copyright 2021 Orion Labs, Inc.

License
=======
AirCoT is licensed under the Apache License, Version 2.0. See LICENSE for details.

Style
=====
1. Prefer double-quotes over single quotes.
2. Prefer spaces over tabs.
3. Follow PEP-8.
4. Follow Google Python Style.
