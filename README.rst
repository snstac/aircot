aircot - Cursor on Target (COT) Classifiers for ADS-B & Aircraft data.
**********************************************************************

AirCOT is a Python Module with functions & methods for Cursor on Target (COT) Event typing/classifying of aircraft
based on ADS-B data.

Examples of software clients using the AirCOT:

* `adsbcot <https://github.com/ampledata/adsbcot>`_: Automatic Dependent Surveillance-Broadcast (ADS-B) to Cursor on Target (CoT) Gateway. Transforms ADS-B position messages to CoT PLI Events.
* `adsbxcot <https://github.com/ampledata/adsbxcot>`_: ADS-B Exchange to Cursor on Target (CoT) Gateway. Transforms ADS-B position messages to CoT PLI Events.
* `stratuxcot <https://github.com/ampledata/stratuxcot>`_: Stratux ADS-B to Cursor on Target (CoT) Gateway. Transforms position messages to CoT PLI Events.


Support Development
===================

**Tech Support**: Email support@undef.net or Signal/WhatsApp: +1-310-621-9598

This tool has been developed for the Disaster Response, Public Safety and
Frontline Healthcare community. This software is currently provided at no-cost
to users. Any contribution you can make to further this project's development
efforts is greatly appreciated.

.. image:: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png
    :target: https://www.buymeacoffee.com/ampledata
    :alt: Support Development: Buy me a coffee!


Requirements
============

AirCOT requires Python 3.6 or above and WILL NOT work on Python versions below 3.6 (that means no Python 2 support).

Installation
============

AirCOT is installed as a dependency for various other programs (see above) but can be installed and updated
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
AirCOT source can be found on Github: https://github.com/ampledata/aircot


Author
======
AirCOT is written and maintained by Greg Albrecht W2GMD oss@undef.net

https://ampledata.org/


Copyright
=========
AirCOT is Copyright 2022 Greg Albrecht


License
=======
Copyright 2022 Greg Albrecht <oss@undef.net>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
